"""Runtime configuration for the Kosciuszko ingestion layer."""

from __future__ import annotations

import os
from importlib.util import find_spec
from pathlib import Path


if find_spec("dotenv") is not None:
    from dotenv import load_dotenv
else:

    def load_dotenv(dotenv_path: str | Path | None = None) -> bool:
        """Small fallback dotenv loader used when python-dotenv is unavailable."""
        env_path = Path(dotenv_path) if dotenv_path is not None else Path(".env")
        if not env_path.exists():
            return False

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, raw_value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue

            os.environ[key] = _clean_env_value(raw_value)

        return True


class Config:
    """Load, validate, and expose application configuration values."""

    def __init__(self):
        # 1. 加载 .env 文件
        # 优先加载 config/ 目录下的 .env，如果不存在则在当前目录寻找
        env_path = Path(__file__).parent.parent / "config" / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()

        # 2. 定义并校验必填项
        # 如果这些配置缺失，程序将直接崩溃并提示具体缺失项
        self.DB_USER = self._get_required_env("DB_USER")
        self.DB_PASSWORD = self._get_required_env("DB_PASSWORD")
        self.DB_DSN = self._get_required_env("DB_DSN")

        # 3. 数据类型转换 (关键：确保 BATCH_SIZE 为整数)
        try:
            self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
        except ValueError as exc:
            raise ValueError("环境变量 BATCH_SIZE 必须为有效的整数。") from exc

        # 4. 可选项与默认值
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.WALLET_LOCATION = os.getenv("WALLET_LOCATION")
        self.WALLET_PASSWORD = os.getenv("WALLET_PASSWORD")

        # 通知系统
        self.PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
        self.PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")

    def _get_required_env(self, key: str) -> str:
        """从环境获取必填配置，缺失则抛出 ValueError。"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"缺少关键环境变量: {key}。请在 .env 文件或系统环境中配置。")
        return value


def _clean_env_value(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


# 实例化以便全局直接导入使用 (可选)
# config = Config()
