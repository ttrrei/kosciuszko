import pytest
from unittest.mock import patch, MagicMock
from src.notifier import Notifier, requests


@pytest.fixture
def mock_config(monkeypatch):
    """模拟通知所需的配置"""
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "PASS")
    monkeypatch.setenv("DB_DSN", "DSN")
    monkeypatch.setenv("PUSHOVER_TOKEN", "mock_token_123")
    monkeypatch.setenv("PUSHOVER_USER_KEY", "mock_user_456")


@patch("requests.post")
def test_send_message_success(mock_post, mock_config):
    """
    测试成功发送消息：
    验证是否向 Pushover API 发送了正确的参数。
    """
    # 模拟 API 返回 200 OK
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notifier = Notifier()
    success = notifier.send("Test Message", title="Kosciuszko Alert")

    assert success is True
    # 验证 POST 请求的参数
    args, kwargs = mock_post.call_args
    assert kwargs["data"]["token"] == "mock_token_123"
    assert kwargs["data"]["user"] == "mock_user_456"
    assert kwargs["data"]["message"] == "Test Message"
    assert kwargs["data"]["title"] == "Kosciuszko Alert"
    assert kwargs["timeout"] == notifier.TIMEOUT_SECONDS


@patch("requests.post")
def test_send_message_with_priority(mock_post, mock_config):
    """
    测试带优先级的消息：
    验证优先级参数是否正确传递。
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notifier = Notifier()
    # 发送紧急消息 (Priority 1)
    notifier.send("Emergency!", priority=1)

    _, kwargs = mock_post.call_args
    assert kwargs["data"]["priority"] == 1


@patch("requests.post")
def test_send_message_failure(mock_post, mock_config):
    """
    测试发送失败处理：
    当 Pushover 返回非 200 状态码时，应返回 False 而不是崩溃。
    """
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_post.return_value = mock_response

    notifier = Notifier()
    success = notifier.send("Failed Message")

    assert success is False


@patch("requests.post")
def test_send_message_network_exception(mock_post, mock_config):
    """
    测试网络异常处理：
    当 requests 抛出异常时，应返回 False 而不是阻塞或崩溃。
    """
    mock_post.side_effect = requests.RequestException("network down")

    notifier = Notifier()
    success = notifier.send("Network Failure")

    assert success is False


def test_missing_credentials(monkeypatch):
    """
    测试缺少凭证的情况：
    如果没有配置 Token，Notifier 应该在初始化或发送时给出警告。
    """
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "PASS")
    monkeypatch.setenv("DB_DSN", "DSN")
    # 清空 Token
    monkeypatch.delenv("PUSHOVER_TOKEN", raising=False)

    notifier = Notifier()
    # 如果没有配置凭证，send 方法应直接返回 False
    assert notifier.send("No Token") is False
