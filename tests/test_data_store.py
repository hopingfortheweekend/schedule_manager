"""
测试数据层 DataStore：验证增删改查逻辑正确性。
每个测试用临时文件，不触碰真实数据。
"""
import os
import tempfile
import pytest

# 把项目根目录加入路径（因为 data_store.py 在根目录）
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_store import DataStore


@pytest.fixture
def store():
    """每个测试用例获得一个干净的 DataStore（临时文件）"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    ds = DataStore(path)
    yield ds
    # 测试结束清理临时文件
    os.remove(path)


class TestTaskOperations:
    """每日任务相关测试"""

    def test_add_and_get(self, store):
        store.add_task("2026-06-11", "写测试代码")
        tasks = store.get_tasks("2026-06-11")
        assert len(tasks) == 1
        assert tasks[0]["task"] == "写测试代码"
        assert tasks[0]["done"] is False

    def test_toggle_task(self, store):
        store.add_task("2026-06-11", "测试切换")
        store.toggle_task("2026-06-11", 0)
        assert store.get_tasks("2026-06-11")[0]["done"] is True
        # 再切回来
        store.toggle_task("2026-06-11", 0)
        assert store.get_tasks("2026-06-11")[0]["done"] is False

    def test_update_task(self, store):
        store.add_task("2026-06-11", "原内容")
        store.update_task("2026-06-11", 0, "新内容")
        assert store.get_tasks("2026-06-11")[0]["task"] == "新内容"

    def test_delete_task(self, store):
        store.add_task("2026-06-11", "待删除")
        store.delete_task("2026-06-11", 0)
        assert store.get_tasks("2026-06-11") == []

    def test_no_crash_on_bad_index(self, store):
        """边界情况：操作不存在的索引不应崩溃"""
        store.toggle_task("2099-01-01", 99)      # 日期不存在
        store.add_task("2026-06-11", "唯一任务")
        store.toggle_task("2026-06-11", 99)      # 索引越界
        store.delete_task("2026-06-11", 99)
        store.update_task("2026-06-11", 99, "xxx")
        # 不应抛出异常


class TestProjectOperations:
    """长期项目相关测试"""

    def test_add_and_get(self, store):
        store.add_project("学习 Python")
        assert "学习 Python" in store.get_projects()

    def test_delete_project(self, store):
        store.add_project("临时项目")
        store.delete_project("临时项目")
        assert "临时项目" not in store.get_projects()

    def test_add_steps_with_deadline(self, store):
        store.add_project("毕设")
        store.add_step("毕设", "写开题报告", "2026-06-15")
        store.add_step("毕设", "做实验", "2026-07-01")

        proj = store.get_project("毕设")
        assert len(proj["steps"]) == 2
        assert proj["steps"][0]["step"] == "写开题报告"
        assert proj["steps"][0]["deadline"] == "2026-06-15"

    def test_toggle_step(self, store):
        store.add_project("测试项目")
        store.add_step("测试项目", "步骤1", "2026-06-20")
        store.toggle_step("测试项目", 0)
        assert store.get_project("测试项目")["steps"][0]["done"] is True

    def test_delete_step(self, store):
        store.add_project("测试项目")
        store.add_step("测试项目", "删掉我", "")
        store.delete_step("测试项目", 0)
        assert len(store.get_project("测试项目")["steps"]) == 0

    def test_update_step(self, store):
        store.add_project("测试项目")
        store.add_step("测试项目", "旧标题", "2026-06-30")
        store.update_step("测试项目", 0, "新标题", "2026-07-15")
        s = store.get_project("测试项目")["steps"][0]
        assert s["step"] == "新标题"
        assert s["deadline"] == "2026-07-15"


class TestCalendarQueries:
    """日历查询相关测试"""

    def test_all_task_dates(self, store):
        store.add_task("2026-06-01", "任务A")
        store.add_task("2026-06-05", "任务B")
        dates = store.get_all_task_dates()
        assert "2026-06-01" in dates
        assert "2026-06-05" in dates

    def test_step_deadlines_only_active(self, store):
        """只有未完成的步骤才出现在截止列表中"""
        store.add_project("P1")
        store.add_step("P1", "未完成步骤", "2026-06-20")
        store.add_step("P1", "已完成步骤", "2026-06-21")
        store.toggle_step("P1", 1)  # 标记第二个为完成

        deadlines = store.get_all_step_deadlines()
        # 只有一个未完成的
        assert len(deadlines) == 1
        assert deadlines[0][1]["step"] == "未完成步骤"

    def test_steps_due_on(self, store):
        store.add_project("P1")
        store.add_step("P1", "赶上这天", "2026-12-25")
        store.add_step("P1", "另一天", "2026-12-26")
        due = store.get_steps_due_on("2026-12-25")
        assert len(due) == 1
        assert due[0][1]["step"] == "赶上这天"


class TestPersistence:
    """数据持久化测试"""

    def test_save_and_reload(self, store):
        store.add_task("2026-08-01", "持久化测试")
        store.add_project("重启项目")
        store.add_step("重启项目", "重启后还在", "2026-09-01")

        # 模拟重启：新建一个 DataStore 指向同一个文件
        store2 = DataStore(store.filepath)
        assert store2.get_tasks("2026-08-01")[0]["task"] == "持久化测试"
        assert "重启项目" in store2.get_projects()
