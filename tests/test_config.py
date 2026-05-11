import os

import pytest

from src.config import Config


@pytest.fixture
def mock_env(monkeypatch):
    """Mock mandatory and typed configuration environment variables."""
    monkeypatch.setenv("DB_USER", "TEST_ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "TEST_PASS")
    monkeypatch.setenv("DB_DSN", "TEST_DSN")
    monkeypatch.setenv("BATCH_SIZE", "20")
    yield monkeypatch


def test_config_loads_correctly(mock_env):
    """测试配置是否能正确加载并转换类型。"""
    config = Config()

    assert config.DB_USER == "TEST_ADMIN"
    assert config.BATCH_SIZE == 20
    assert isinstance(config.BATCH_SIZE, int)


def test_missing_mandatory_config(monkeypatch):
    """测试当缺失必填项（如 DB_PASSWORD）时，是否抛出异常。"""
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_DSN", "DSN")
    if "DB_PASSWORD" in os.environ:
        monkeypatch.delenv("DB_PASSWORD")

    with pytest.raises(ValueError) as excinfo:
        Config()

    assert "DB_PASSWORD" in str(excinfo.value)


def test_default_values(monkeypatch):
    """测试可选配置是否有默认值。"""
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "PASS")
    monkeypatch.setenv("DB_DSN", "DSN")
    if "LOG_LEVEL" in os.environ:
        monkeypatch.delenv("LOG_LEVEL")

    config = Config()

    assert config.LOG_LEVEL == "INFO"
