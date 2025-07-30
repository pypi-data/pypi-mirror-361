
import contextlib
import sqlite3


@contextlib.contextmanager
def db_connection(DB_NAME: str = 'r.db') -> sqlite3.Connection:
    """上下文管理器用于数据库连接管理"""
    conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row  # 允许以字典方式访问结果
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()