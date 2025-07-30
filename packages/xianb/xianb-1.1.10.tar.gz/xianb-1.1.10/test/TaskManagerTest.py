import unittest
import json
from datetime import datetime
from xianbao.core.Task import TaskManager
from xianbao.core.SQLiteOp import db_connection


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """在每个测试前初始化一个内存数据库"""
        self.task_manager = TaskManager(table_name="tasks")
        self.task_manager.initialize_db()

    def test_01_initialize_db(self):
        """验证表结构和索引是否存在"""
        with db_connection() as cursor:
            # 查询表信息
            cursor.execute("PRAGMA table_info(tasks)")
            columns = {row[1] for row in cursor.fetchall()}
            expected_columns = {
                "id", "status", "meta", "created_time", "updated_time", "business_type"
            }
            self.assertTrue(expected_columns.issubset(columns))

            # 验证索引存在
            cursor.execute("PRAGMA index_list(tasks)")
            indexes = {idx[1] for idx in cursor.fetchall()}
            expected_indexes = {"idx_status", "idx_business_type", "idx_created_time"}
            self.assertTrue(expected_indexes.issubset(indexes))

    def test_02_add_task(self):
        """测试添加任务"""
        meta = {"order_id": "12345", "customer": "Alice"}
        task_id = self.task_manager.add_task(meta=meta, business_type="order_processing")
        self.assertGreater(task_id, 0)

        task = self.task_manager.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["status"], 0)
        self.assertEqual(task["meta"], meta)
        self.assertEqual(task["business_type"], "order_processing")

    def test_03_update_status(self):
        """测试更新状态"""
        task_id = self.task_manager.add_task(meta={}, business_type="test")
        updated = self.task_manager.update_status(task_id, 10)
        self.assertTrue(updated)

        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["status"], 10)

    def test_04_update_status_and_meta(self):
        """测试同时更新状态和 meta"""
        task_id = self.task_manager.add_task(meta={"a": 1}, business_type="test")
        new_meta = {"b": 2}
        updated = self.task_manager.update_status_and_meta(task_id, 2, new_meta)
        self.assertTrue(updated)

        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["status"], 2)
        self.assertEqual(task["meta"], new_meta)

    def test_05_list_tasks_by_status(self):
        """测试按状态分页查询"""
        for i in range(15):
            self.task_manager.add_task(meta={}, business_type="test")

        tasks = self.task_manager.list_tasks_by_status(status=0, page=1, per_page=10)
        self.assertEqual(len(tasks), 10)

        tasks_page2 = self.task_manager.list_tasks_by_status(status=0, page=2, per_page=10)
        self.assertEqual(len(tasks_page2), 5)

    def test_06_count_by_status(self):
        """测试统计指定状态的任务数量"""
        for _ in range(5):
            self.task_manager.add_task(meta={}, business_type="test")
        count = self.task_manager.count_by_status(0)
        self.assertEqual(count, 5)

    def test_07_get_task(self):
        """测试根据ID获取任务"""
        task_id = self.task_manager.add_task(meta={"name": "Test"}, business_type="test")
        task = self.task_manager.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["meta"]["name"], "Test")

    def test_08_batch_update_status(self):
        """测试批量更新状态"""
        ids = [self.task_manager.add_task(meta={}, business_type="test") for _ in range(3)]
        updated = self.task_manager.batch_update_status(ids, 1)
        self.assertEqual(updated, 3)

        for task_id in ids:
            task = self.task_manager.get_task(task_id)
            self.assertEqual(task["status"], 1)

    def test_09_delete_task(self):
        """测试删除任务"""
        task_id = self.task_manager.add_task(meta={}, business_type="test")
        deleted = self.task_manager.delete_task(task_id)
        self.assertTrue(deleted)

        task = self.task_manager.get_task(task_id)
        self.assertIsNone(task)

    def test_10_health_check(self):
        """测试健康检查"""
        healthy, msg = self.task_manager.health_check()
        self.assertTrue(healthy)
        self.assertEqual(msg, "Database is healthy")

    def test_11_list_all_tasks(self):
        """测试列出所有任务"""
        for _ in range(15):
            self.task_manager.add_task(meta={}, business_type="test")

        tasks = self.task_manager.list_all_tasks(page=1, per_page=10)
        self.assertEqual(len(tasks), 10)

        tasks_page2 = self.task_manager.list_all_tasks(page=2, per_page=10)
        self.assertEqual(len(tasks_page2), 5)

    def test_12_count_all_tasks(self):
        """测试统计总任务数"""
        for _ in range(7):
            self.task_manager.add_task(meta={}, business_type="test")
        count = self.task_manager.count_all_tasks()
        self.assertEqual(count, 7)

    def test_13_advanced_search(self):
        """测试高级搜索功能"""
        base_time = datetime.now().strftime("%Y-%m-%d")
        meta = {"product": "chair"}

        task1 = self.task_manager.add_task(meta=meta, business_type="furniture")
        task2 = self.task_manager.add_task(meta=meta, business_type="electronics")

        results, total = self.task_manager.advanced_search(
            status=0,
            created_start=base_time,
            meta_contains={"product": "chair"},
            page=1,
            per_page=5
        )
        self.assertEqual(total, 2)
        self.assertEqual(len(results), 2)

    def test_14_list_tasks_created_between(self):
        """测试时间范围查询"""
        now = datetime.now()
        task1 = self.task_manager.add_task(meta={}, business_type="test")
        task2 = self.task_manager.add_task(meta={}, business_type="test")

        start = now.replace(second=0, microsecond=0)
        end = now.replace(second=59, microsecond=999999)

        tasks = self.task_manager.list_tasks_created_between(start, end)
        self.assertIn(task1, [t['id'] for t in tasks])
        self.assertIn(task2, [t['id'] for t in tasks])

    def test_15_list_tasks_by_business_type(self):
        """测试按业务类型分页查询"""
        for _ in range(3):
            self.task_manager.add_task(meta={}, business_type="finance")
        for _ in range(2):
            self.task_manager.add_task(meta={}, business_type="hr")

        tasks = self.task_manager.list_tasks_by_business_type("finance", page=1, per_page=2)
        self.assertEqual(len(tasks), 2)

    def test_16_count_tasks_by_business_type(self):
        """测试按业务类型统计数量"""
        for _ in range(4):
            self.task_manager.add_task(meta={}, business_type="finance")
        count = self.task_manager.count_tasks_by_business_type("finance")
        self.assertEqual(count, 4)

    def test_17_execute_custom_sql(self):
        """测试自定义SQL查询"""
        self.task_manager.add_task(meta={}, business_type="custom")
        result = self.task_manager.execute_custom_sql("SELECT * FROM tasks WHERE business_type = ?", ("custom",))
        self.assertEqual(len(result), 1)

    def test_18_execute_custom_update(self):
        """测试自定义SQL写入操作"""
        task_id = self.task_manager.add_task(meta={}, business_type="custom")
        rows = self.task_manager.execute_custom_update(
            "UPDATE tasks SET business_type = ? WHERE id = ?", ("updated", task_id)
        )
        self.assertEqual(rows, 1)

        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["business_type"], "updated")


if __name__ == "__main__":
    unittest.main()
