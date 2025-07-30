import sqlite3
import portalocker
import os
import threading
import time
from contextlib import contextmanager
from queue import Empty, Full
import logging


class SQLiteProcessQueue:
    """
    多进程安全的SQLite阻塞队列

    特性：
    - 进程安全的数据库连接管理
    - 基于文件锁的进程间协调
    - 可选的队列大小限制
    - 高效的数据获取策略
    - 指数退避的等待机制
    - 数据库维护功能

    Note: 每个进程应创建自己的队列实例，指向同一个数据库文件
    """

    def __init__(self, db_path='rpa_ztdb.db', table_name='queue',
                 max_size=10000, timeout=30.0,
                 lock_path='rpa_queue',
                 journal_mode='WAL', busy_timeout=5000,
                 poll_interval=0.1, max_poll_interval=1.0):
        """
        初始化多进程队列

        :param db_path: SQLite数据库文件路径
        :param table_name: 队列表名
        :param max_size: 队列最大容量(可选)
        :param timeout: 默认操作超时时间(秒)
        :param journal_mode: SQLite日志模式(WAL/DELETE等)
        :param busy_timeout: 数据库忙等待超时(毫秒)
        :param poll_interval: 队列空时初始轮询间隔(秒)
        :param max_poll_interval: 最大轮询间隔(秒)
        :param lock_path: 锁文件
        """
        self.lock_path = lock_path + '.lok'
        self.db_path = os.path.abspath(db_path)
        self.table_name = table_name
        self.max_size = max_size
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_poll_interval = max_poll_interval
        self.journal_mode = journal_mode
        self.busy_timeout = busy_timeout
        self.fd = None

        # 为每个进程创建独立的数据库连接
        self.conn = None

        # 初始化数据库结构
        self._init_db()

    @contextmanager
    def _db_connection(self):
        """进程安全的数据库连接上下文管理"""
        try:
            if self.conn is None:
                # 创建数据库目录(如果需要)
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

                # 创建新连接
                self.conn = sqlite3.connect(
                    self.db_path,
                    timeout=self.busy_timeout / 1000,
                    isolation_level=None  # 使用自动提交模式
                )

                # 优化设置
                self.conn.execute(f'PRAGMA journal_mode={self.journal_mode}')
                self.conn.execute('PRAGMA synchronous=NORMAL')
            yield self.conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                raise BusyError("Database is locked") from e
            raise
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            raise
        finally:
            # 不关闭连接，保持打开状态供后续使用
            pass

    def _init_db(self):
        """初始化数据库结构"""
        with self._db_connection() as conn:
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data BLOB NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            # 加速消费查询
            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_order ON {self.table_name}(id ASC);')
            # 检查点清理
            conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')

    def _file_lock(self, timeout=10.0):
        """基于文件的锁，用于进程间协调"""
        start_time = time.monotonic()
        while True:
            try:
                # 尝试创建锁文件
                self.fd = open(self.lock_path, 'w')
                portalocker.lock(self.fd, portalocker.LOCK_EX)
                return
            except FileExistsError:
                # 检查超时
                if time.monotonic() - start_time > timeout:
                    raise TimeoutError("File lock timeout")
                # 指数退避等待
                time.sleep(min(0.1 * (2 ** int((time.monotonic() - start_time) / 0.1)), 0.6))
            except Exception as e:
                logging.error(f"File lock error: {e}")
                raise

    def _file_unlock(self):
        """释放文件锁"""
        try:
            if hasattr(self, 'fd'):
                portalocker.unlock(self.fd)
                self.fd.close()
                print("Lock file removed", threading.currentThread().name)
        except Exception as e:
            logging.warning(f"Failed to remove lock file: {e}")

    def put(self, item: bytes, block=True, timeout=None):
        """
        将项目放入队列

        :param item: 要放入队列的数据(bytes)
        :param block: 如果队列满是否阻塞
        :param timeout: 阻塞超时时间(秒)
        :raises Full: 队列满且不阻塞或超时时
        """
        if not isinstance(item, bytes):
            raise TypeError("Only bytes are supported")

        timeout = timeout or self.timeout
        start_time = time.monotonic()
        poll_interval = self.poll_interval

        while True:
            # 检查队列大小(使用文件锁确保准确)
            try:
                self._file_lock()
                current_size = self.qsize()

                # 检查队列是否已满
                if self.max_size is not None and current_size >= self.max_size:
                    if not block:
                        raise Full("Queue full")

                    # 检查超时
                    elapsed = time.monotonic() - start_time
                    if elapsed >= timeout:
                        raise Full("Queue full")
                    self._file_unlock()  # 等待前释放锁
                    # 等待并重试
                    time.sleep(poll_interval)
                    poll_interval = min(poll_interval * 2, self.max_poll_interval)
                    continue

                # 有空间，执行插入
                with self._db_connection() as conn:
                    conn.execute(
                        f'INSERT INTO {self.table_name} (data) VALUES (?)',
                        (item,)
                    )
                return
            finally:
                self._file_unlock()

    def get(self, block=True, timeout=None) -> bytes:
        """
        从队列中获取并移除项目

        :param block: 如果队列空是否阻塞
        :param timeout: 阻塞超时时间(秒)
        :return: 从队列中获取的数据(bytes)
        :raises Empty: 队列空且不阻塞或超时时
        """
        timeout = timeout or self.timeout
        start_time = time.monotonic()
        poll_interval = self.poll_interval

        while True:
            try:
                # 获取文件锁
                self._file_lock()

                # 尝试获取数据
                with self._db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        f'DELETE FROM {self.table_name} '
                        'WHERE id = (SELECT id FROM {0} ORDER BY id ASC LIMIT 1) '
                        'RETURNING data'.format(self.table_name)
                    )
                    result = cursor.fetchone()
                    if result:
                        return result[0]

                # 队列为空，检查阻塞设置
                if not block:
                    raise Empty("Queue empty")

                # 检查超时
                elapsed = time.monotonic() - start_time
                if elapsed >= timeout:
                    raise Empty("Queue empty")

                # 等待并重试
                time.sleep(poll_interval)
                poll_interval = min(poll_interval * 2, self.max_poll_interval)
            finally:
                self._file_unlock()

    def qsize(self) -> int:
        """返回队列中的项目数"""
        with self._db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
            return cursor.fetchone()[0]

    def empty(self) -> bool:
        """如果队列为空返回True，否则False"""
        return self.qsize() == 0

    def full(self) -> bool:
        """如果队列满返回True，否则False"""
        if self.max_size is None:
            return False
        return self.qsize() >= self.max_size

    def clear(self):
        """清空队列"""
        try:
            self._file_lock()
            with self._db_connection() as conn:
                conn.execute(f'DELETE FROM {self.table_name}')
        finally:
            self._file_unlock()

    def vacuum(self):
        """回收数据库空间"""
        try:
            self._file_lock()
            with self._db_connection() as conn:
                conn.execute('VACUUM')
        finally:
            self._file_unlock()

    def maintenance(self):
        """执行数据库维护任务"""
        try:
            self._file_lock()
            with self._db_connection() as conn:
                # WAL检查点
                conn.execute('PRAGMA wal_checkpoint(TRUNCATE);')

                # 重新构建索引
                conn.execute(f'REINDEX {self.table_name}')
        finally:
            self._file_unlock()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
            finally:
                self.conn = None


class BusyError(Exception):
    """数据库忙异常"""
    pass



