import pytest
from unittest.mock import MagicMock, patch
from src.db_operator import DbOperator


@pytest.fixture
def mock_config(monkeypatch):
    """模拟基础配置"""
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "mock_pass")
    monkeypatch.setenv("DB_DSN", "mock_dsn")
    monkeypatch.setenv("BATCH_SIZE", "10")


def test_singleton_pattern(mock_config):
    """
    测试单例模式：
    无论实例化多少次，DbOperator 应该始终返回同一个对象。
    """
    db1 = DbOperator()
    db2 = DbOperator()
    assert db1 is db2


@patch("oracledb.create_pool")
def test_get_connection_pool_init(mock_create_pool, mock_config):
    """
    测试连接池初始化：
    验证在第一次调用时是否正确调用了 oracledb 的创建连接池方法。
    """
    db = DbOperator()
    # 触发连接池初始化逻辑（假设有一个内部方法获取连接）
    db.get_connection()
    assert mock_create_pool.called


def test_execute_merge_chunking(mock_config):
    """
    测试分批写入逻辑（关键）：
    如果输入 25 条记录，BATCH_SIZE 为 10，
    内部执行合并的方法应该被调用 3 次 (10, 10, 5)。
    """
    db = DbOperator()

    # 模拟底层的数据库执行方法
    db._raw_merge_execute = MagicMock()

    # 准备 25 条模拟数据
    mock_data = [{"CODE": f"STK{i}", "PRICE": 10.5} for i in range(25)]

    # 执行业务逻辑
    db.execute_merge(target_table="ODS_YAHOO", data=mock_data)

    # 验证是否分了 3 批执行
    assert db._raw_merge_execute.call_count == 3
