
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from xianbao.core.SQLiteOp import db_connection


class TaskManager:
    """RPA任务数据库管理器"""

    def __init__(self, db_name: str = "rpa_ztdb.db", table_name: str = "tasks") -> None:
        """初始化任务管理器
        Args:
            db_name: 数据库文件名，默认为 "rpa_ztdb.db"
            table_name: 表名，默认为 "tasks"
        """
        self.DB_NAME = db_name
        self.TABLE_NAME = table_name
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def initialize_db(self) -> None:
        """初始化数据库和表结构"""
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status INTEGER NOT NULL DEFAULT 0,  -- 使用整数代替文本
                meta TEXT NOT NULL,
                created_time TEXT NOT NULL,
                updated_time TEXT NOT NULL,
                business_type TEXT
            )
            """)
            # 索引
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_status ON {self.TABLE_NAME}(status)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_business_type ON {self.TABLE_NAME}(business_type)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_created_time ON {self.TABLE_NAME}(created_time)")

    def add_task(self, meta: Dict, business_type: str, status: int = 0) -> int:
        """添加新任务（使用完整时间格式）"""
        now = datetime.now().strftime(self.TIME_FORMAT)  # 使用完整时间格式

        meta_json = json.dumps(meta)

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"INSERT INTO {self.TABLE_NAME} (status, meta, created_time, updated_time, business_type) "
                "VALUES (?, ?, ?, ?, ?)",
                (status, meta_json, now, now, business_type)
            )
            return cursor.lastrowid

    def update_status(self, task_id: int, new_status: int) -> bool:
        """原子性更新任务状态
        Args:
            task_id: 任务ID
            new_status: 新状态

        Returns:
            更新是否成功
        """
        now = datetime.now().strftime(self.TIME_FORMAT)

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"UPDATE {self.TABLE_NAME} SET status = ?, updated_time = ? "
                "WHERE id = ?",
                (new_status, now, task_id)
            )
            return cursor.rowcount > 0

    def update_status_and_meta(self, task_id: int, new_status: int, new_meta: Dict) -> bool:
        """
        同时更新任务状态和 meta 字段

        Args:
            task_id: 任务ID
            new_status: 新状态值
            new_meta: 更新后的 meta 数据（字典格式）

        Returns:
            是否成功更新任务
        """
        now = datetime.now().strftime(self.TIME_FORMAT)
        meta_json = json.dumps(new_meta)

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"UPDATE {self.TABLE_NAME} SET status = ?, meta = ?, updated_time = ? WHERE id = ?",
                (new_status, meta_json, now, task_id)
            )
            return cursor.rowcount > 0

    def list_tasks_by_status(
            self,
            status: int,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """根据状态分页查询任务
        Args:
            status: 状态值
            page: 页码(1-based)
            per_page: 每页数量
            order_by: 排序字段
            ascending: 是否升序

        Returns:
            任务字典列表(包含反序列化的meta)
        """
        offset = (page - 1) * per_page
        order_direction = "ASC" if ascending else "DESC"

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT id, status, meta, created_time, updated_time, business_type "
                f"FROM {self.TABLE_NAME} "
                f"WHERE status = ? "
                f"ORDER BY {order_by} {order_direction} "
                "LIMIT ? OFFSET ?",
                (status, per_page, offset)
            )

            tasks = []
            for row in cursor.fetchall():
                task = dict(row)
                task["meta"] = json.loads(task["meta"])
                task["business_type"] = task.get("business_type")
                tasks.append(task)
            return tasks

    def count_by_status(self, status: int) -> int:
        """获取指定状态的记录数量
        Args:
            status: 状态值

        Returns:
            记录数量
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE status = ?",
                (status,)
            )
            return cursor.fetchone()[0]

    def get_task(self, task_id: int) -> Optional[Dict]:
        """根据ID获取单个任务详情"""
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT * FROM {self.TABLE_NAME} WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            task = dict(row)
            task["meta"] = json.loads(task["meta"])
            task["business_type"] = task.get("business_type")
            return task

    def batch_update_status(self, task_ids: List[int], new_status: int) -> int:
        """批量更新任务状态
        Args:
            task_ids: 任务ID列表
            new_status: 新状态

        Returns:
            更新的记录数
        """
        if not task_ids:
            return 0

        now = datetime.now().strftime(self.TIME_FORMAT)  # 使用完整时间格式
        id_placeholders = ','.join(['?'] * len(task_ids))

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"UPDATE {self.TABLE_NAME} SET status = ?, updated_time = ? "
                f"WHERE id IN ({id_placeholders})",
                (new_status, now, *task_ids)
            )
            return cursor.rowcount

    def delete_task(self, task_id: int) -> bool:
        """删除指定任务
        Args:
            task_id: 任务ID

        Returns:
            是否成功删除
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE id = ?",
                (task_id,)
            )
            return cursor.rowcount > 0

    def health_check(self) -> Tuple[bool, str]:
        """数据库健康检查
        Returns:
            (健康状态, 状态信息)
        """
        try:
            with db_connection(self.DB_NAME) as cursor:
                cursor.execute(f"SELECT 1 FROM {self.TABLE_NAME} LIMIT 1")
            return True, "Database is healthy"
        except Exception as e:
            return False, f"Database error: {str(e)}"

    def list_all_tasks(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: str = "id",
            ascending: bool = True
    ) -> List[Dict]:
        """分页查询所有任务（无状态过滤）

        Args:
            page: 页码(1-based)
            per_page: 每页数量
            order_by: 排序字段
            ascending: 是否升序

        Returns:
            任务字典列表(包含反序列化的meta)
        """
        offset = (page - 1) * per_page
        order_direction = "ASC" if ascending else "DESC"

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT id, status, meta, created_time, updated_time, business_type "
                f"FROM {self.TABLE_NAME} "
                f"ORDER BY {order_by} {order_direction} "
                "LIMIT ? OFFSET ?",
                (per_page, offset)
            )

            tasks_data = []
            for row in cursor.fetchall():
                task = dict(row)
                task["meta"] = json.loads(task["meta"])
                task["business_type"] = task.get("business_type")
                tasks_data.append(task)
            return tasks_data

    def count_all_tasks(self) -> int:
        """获取整个表格的总记录数

        Returns:
            表格中的总记录数量
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {self.TABLE_NAME}")
            return cursor.fetchone()[0]

    def advanced_search(
            self,
            status: Optional[int] = None,
            created_start: Optional[str] = None,
            created_end: Optional[str] = None,
            meta_contains: Optional[Dict] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Tuple[List[Dict], int]:
        """高级分页搜索（支持多种条件）

        Args:
            status: 任务状态过滤
            created_start: 创建时间开始(yyyy-MM-dd)
            created_end: 创建时间结束(yyyy-MM-dd)
            meta_contains: meta中应包含的键值对
            page: 页码
            per_page: 每页数量

        Returns:
            (匹配任务列表, 匹配总数量)
        """
        offset = (page - 1) * per_page
        conditions = []
        params = []

        # 构建查询条件
        if status:
            conditions.append("status = ?")
            params.append(int(status))

        if created_start:
            conditions.append("created_time >= ?")
            params.append(created_start + " 00:00:00")  # 添加时间部分以涵盖全天

        if created_end:
            conditions.append("created_time <= ?")
            params.append(created_end + " 23:59:59")  # 添加时间部分以涵盖全天

        # 处理JSON字段查询
        if meta_contains:
            for key, value in meta_contains.items():
                # JSON路径查找: $.key = value
                conditions.append(f"json_extract(meta, '$.\"{key}\"') = ?")
                params.append(str(value))

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with db_connection(self.DB_NAME) as cursor:
            # 查询总数
            count_query = f"SELECT COUNT(*) FROM {self.TABLE_NAME} {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # 查询分页数据
            data_query = (
                f"SELECT id, status, meta, created_time, updated_time, business_type "
                f"FROM {self.TABLE_NAME} {where_clause} "
                f"ORDER BY created_time DESC "
                f"LIMIT ? OFFSET ?"
            )
            cursor.execute(data_query, params + [per_page, offset])

            tasks_data = []
            for row in cursor.fetchall():
                task = dict(row)
                task["meta"] = json.loads(task["meta"])
                task["business_type"] = task.get("business_type")
                tasks_data.append(task)

            return tasks_data, total_count

    def parse_datetime(self, dt_str: str) -> datetime:
        """将数据库时间字符串解析为datetime对象
        Args:
            dt_str: 格式为yyyy-MM-dd HH:mm:ss的字符串

        Returns:
            datetime对象
        """
        return datetime.strptime(dt_str, self.TIME_FORMAT)

    def format_datetime(self, dt: datetime) -> str:
        """将datetime对象格式化为数据库字符串
        Args:
            dt: datetime对象

        Returns:
            格式为yyyy-MM-dd HH:mm:ss的字符串
        """
        return dt.strftime(self.TIME_FORMAT)

    def list_tasks_created_between(self, start: datetime, end: datetime) -> List[Dict]:
        """查询在指定时间范围内创建的任务
        Args:
            start: 开始时间（datetime对象）
            end: 结束时间（datetime对象）

        Returns:
            任务列表
        """
        start_str = self.format_datetime(start)
        end_str = self.format_datetime(end)

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT * FROM {self.TABLE_NAME} "
                "WHERE created_time BETWEEN ? AND ? "
                "ORDER BY created_time",
                (start_str, end_str)
            )

            tasks_data = []
            for row in cursor.fetchall():
                task = dict(row)
                task["meta"] = json.loads(task["meta"])
                task["business_type"] = task.get("business_type")
                # 添加解析后的datetime对象到结果
                task["created_datetime"] = self.parse_datetime(task["created_time"])
                task["updated_datetime"] = self.parse_datetime(task["updated_time"])
                tasks_data.append(task)
            return tasks_data

    def list_tasks_by_business_type(
        self,
        business_type: str,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "id",
        ascending: bool = True
    ) -> List[Dict]:
        """根据业务类型分页查询任务"""
        offset = (page - 1) * per_page
        order_direction = "ASC" if ascending else "DESC"

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT id, status, meta, created_time, updated_time, business_type "
                f"FROM {self.TABLE_NAME} "
                f"WHERE business_type = ? "
                f"ORDER BY {order_by} {order_direction} "
                "LIMIT ? OFFSET ?",
                (business_type, per_page, offset)
            )

            tasks = []
            for row in cursor.fetchall():
                task = dict(row)
                task["meta"] = json.loads(task["meta"])
                tasks.append(task)
            return tasks

    def count_tasks_by_business_type(self, business_type: str) -> int:
        """获取指定业务类型的记录数量"""
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.TABLE_NAME} WHERE business_type = ?",
                (business_type,)
            )
            return cursor.fetchone()[0]

    def execute_custom_sql(self, sql: str, params: tuple = ()) -> List[Dict]:
        """
        执行自定义SQL查询（适用于 SELECT 操作）

        Args:
            sql: 完整的SQL查询语句
            params: SQL参数化查询所需的参数元组

        Returns:
            查询结果列表，每条记录为字典格式
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # 将结果转换为字典形式
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def execute_custom_update(self, sql: str, params: tuple = ()) -> int:
        """
        执行自定义SQL写入操作（适用于 INSERT/UPDATE/DELETE）

        Args:
            sql: 完整的SQL语句
            params: 参数化值

        Returns:
            受影响的行数
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
