
from typing import Dict, List, Optional
from xianbao.core.SQLiteOp import db_connection


class DictManager:
    """数据字典管理类"""

    def __init__(self, db_name: str = "rpa_ztdb.db") -> None:
        """初始化数据字典管理器
        Args:
            db_name: SQLite数据库文件名，默认为 "rpa_ztdb.db"
        """
        self.DB_NAME = db_name
        self.initialize()

    def initialize(self) -> None:
        """初始化数据字典表结构"""
        with db_connection(self.DB_NAME) as cursor:
            # 创建字典类型表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sys_dict_type (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                `name` TEXT NOT NULL,        -- 字典类型名称（如：性别字典）
                code TEXT NOT NULL UNIQUE, -- 字典类型编码（如：gender）
                description TEXT           -- 字典类型描述
            )
            """)

            # 创建字典项表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sys_dict_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                `key` TEXT NOT NULL,         -- 字典项键（如：M）
                `value` TEXT NOT NULL,       -- 字典项值（如：男）
                type_id INTEGER NOT NULL,  -- 关联的字典类型ID
                sort_order INTEGER DEFAULT 0, -- 排序顺序
                FOREIGN KEY (type_id) REFERENCES sys_dict_type(id)
            )
            """)

            # 创建索引优化查询
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_dict_type_code ON sys_dict_type(code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dict_data_type_id ON sys_dict_data(type_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dict_data_key ON sys_dict_data(key)")

    # 字典类型管理
    def add_dict_type(self, name: str, code: str, description: str = "") -> int:
        """添加字典类型
        Args:
            name: 字典类型名称
            code: 字典类型编码（唯一标识）
            description: 类型描述（可选）
            
        Returns:
            新字典类型的ID
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                "INSERT INTO sys_dict_type (name, code, description) "
                "VALUES (?, ?, ?)",
                (name, code, description)
            )
            return cursor.lastrowid

    def get_dict_type_by_code(self, code: str) -> Optional[Dict]:
        """根据编码获取字典类型
        Args:
            code: 字典类型编码
            
        Returns:
            字典类型信息（字典形式）或 None
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                "SELECT id, name, code, description FROM sys_dict_type "
                "WHERE code = ?",
                (code,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_all_dict_types(self) -> List[Dict]:
        """获取所有字典类型
        Returns:
            字典类型列表
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(
                "SELECT id, name, code, description FROM sys_dict_type "
                "ORDER BY id"
            )
            return [dict(row) for row in cursor.fetchall()]

    # 字典项管理
    def add_dict_item(
            self,
            type_code: str,
            key: str,
            value: str,
            sort_order: int = 0
    ) -> int:
        """添加字典项到指定类型的字典
        Args:
            type_code: 字典类型编码
            key: 字典项键
            value: 字典项值
            sort_order: 排序序号（可选）
            
        Returns:
            新字典项的ID
        """
        with db_connection(self.DB_NAME) as cursor:
            # 获取字典类型ID
            cursor.execute(
                "SELECT id FROM sys_dict_type WHERE code = ?",
                (type_code,)
            )
            type_row = cursor.fetchone()

            if not type_row:
                raise ValueError(f"字典类型不存在: {type_code}")

            type_id = type_row[0]

            cursor.execute(
                "INSERT INTO sys_dict_data (key, value, type_id, sort_order) "
                "VALUES (?, ?, ?, ?)",
                (key, value, type_id, sort_order)
            )
            return cursor.lastrowid

    def get_dict_items(self, type_code: str) -> List[Dict]:
        """根据字典类型编码获取所有字典项
        Args:
            type_code: 字典类型编码
            
        Returns:
            按sort_order排序的字典项列表
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute("""
            SELECT d.key, d.value, d.sort_order 
            FROM sys_dict_data d
            JOIN sys_dict_type t ON d.type_id = t.id
            WHERE t.code = ?
            ORDER BY d.sort_order, d.id
            """, (type_code,))

            return [
                {"key": row[0], "value": row[1], "order": row[2]}
                for row in cursor.fetchall()
            ]

    def get_dict_value(self, type_code: str, key: str) -> Optional[str]:
        """获取指定字典类型和键对应的值
        Args:
            type_code: 字典类型编码
            key: 字典项键
            
        Returns:
            字典项值，如果不存在则返回None
        """
        with db_connection(self.DB_NAME) as cursor:
            cursor.execute("""
            SELECT d.value 
            FROM sys_dict_data d
            JOIN sys_dict_type t ON d.type_id = t.id
            WHERE t.code = ? AND d.key = ?
            """, (type_code, key))

            row = cursor.fetchone()
            return row[0] if row else None

    def update_dict_item(
            self,
            type_code: str,
            key: str,
            new_value: str,
            new_sort_order: Optional[int] = None
    ) -> bool:
        """更新字典项
        Args:
            type_code: 字典类型编码
            key: 字典项键
            new_value: 新的字典项值
            new_sort_order: 新的排序序号（可选）
            
        Returns:
            是否成功更新
        """
        set_clause = "value = ?"
        params = [new_value]

        if new_sort_order is not None:
            set_clause += ", sort_order = ?"
            params.append(new_sort_order)

        with db_connection(self.DB_NAME) as cursor:
            cursor.execute(f"""
            UPDATE sys_dict_data 
            SET {set_clause}
            WHERE id IN (
                SELECT d.id
                FROM sys_dict_data d
                JOIN sys_dict_type t ON d.type_id = t.id
                WHERE t.code = ? AND d.key = ?
            )
            """, (*params, type_code, key))

            return cursor.rowcount > 0

    # 高级功能
    def get_dict_as_mapping(self, type_code: str) -> Dict[str, str]:
        """将字典类型的所有项转换为字典映射
        Args:
            type_code: 字典类型编码

        Returns:
            {键: 值} 的字典
        """
        items = self.get_dict_items(type_code)
        return {item["key"]: item["value"] for item in items}

    def get_dict_lookup(self, type_code: str) -> Dict[str, str]:
        """获取反向字典（值到键的映射）
        Args:
            type_code: 字典类型编码
            
        Returns:
            {值: 键} 的字典
        """
        items = self.get_dict_items(type_code)
        return {item["value"]: item["key"] for item in items}


if __name__ == '__main__':
    # 创建字典管理器实例
    dict_manager = DictManager()


    # 创建新的字典类型
    user_type_id = dict_manager.add_dict_type(
        name="用户类型",
        code="user_type",
        description="用户类型分类"
    )

    # 添加字典项
    dict_manager.add_dict_item("user_type", "ADMIN", "管理员", 1)
    dict_manager.add_dict_item("user_type", "USER", "普通用户", 2)

    # 获取字典类型信息
    user_type = dict_manager.get_dict_type_by_code("user_type")
    if user_type:
        print(f"字典类型: {user_type['name']}({user_type['code']})")
    else:
        print("未找到用户类型字典")

    # 查询字典项列表
    status_items = dict_manager.get_dict_items("status")
    for item in status_items:
        print(f"{item['key']} => {item['value']}")

    # 获取单个值
    file_desc = dict_manager.get_dict_value("file_type", "pdf")
    print(f"PDF文件的描述: {file_desc}")  # 输出: PDF文档

    # 高级映射
    status_mapping = dict_manager.get_dict_as_mapping("status")
    print(status_mapping["INIT"])  # 输出: 初始状态

    # 反向查询
    status_lookup = dict_manager.get_dict_lookup("status")
    print(status_lookup["成功"])  # 输出: SUCC