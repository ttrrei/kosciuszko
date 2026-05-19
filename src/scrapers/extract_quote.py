import os
import json
import logging
from datetime import datetime
from src.scrapers.http_client import HttpClient

logger = logging.getLogger(__name__)


class ExtractQuote(HttpClient):
    def __init__(self):
        super().__init__()
        profile_path = os.path.join("config", "scrapers_profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)["yahoo"]

        self.target_table = self.profile["target_table"]
        self.primary_keys = self.profile["primary_keys"]
        self.period = self.profile.get("period", "60d")
        self.interval = self.profile.get("interval", "1h")

    def process_symbol(self, symbol):
        symbol_upper = symbol.upper()
        save_path = f"data/samples/yahoo/{symbol_upper}.json"
        records_raw = None

        # --- 双轨策略一：离线 TDD 快照优先 ---
        # 如果本地存在你通过全新方式下载的真实物理快照，直接加载，彻底不依赖外部网络
        if os.path.exists(save_path):
            logger.info(f"Loading offline snapshot from {save_path}")
            with open(save_path, "r", encoding="utf-8") as f:
                records_raw = json.load(f)
        else:
            # --- 双轨策略二：生产环境下在线调用你跑通的 yfinance 逻辑 ---
            import yfinance as yf
            import pandas as pd
            ticker = f"{symbol_upper}.AX"
            logger.info(f"Fetching live data from yfinance for {ticker}")
            try:
                df = yf.download(
                    ticker,
                    period=self.period,
                    interval=self.interval,
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
                if df is None or df.empty:
                    logger.error(f"Yahoo returned empty dataframe for {ticker}")
                    return None

                df = df.reset_index()
                # 兼容未来可能出现的 MultiIndex 列名扁平化
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ["_".join([str(x) for x in col if x]) for col in df.columns.values]

                for col in df.columns:
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].astype(str)

                records_raw = df.to_dict(orient="records")

                # 在生产环境调试模式下自动对线上真实请求持久化快照
                if self.config.get('debug'):
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(records_raw, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"yfinance runtime engine failed for {ticker}: {e}")
                return None

        if not records_raw:
            return None

        # --- 弹性动态解析与标准契约转化 ---
        records = []
        for row in records_raw:
            # yfinance 导出的时间列通常为 'Datetime' 或 'Date'
            date_str = row.get("Datetime") or row.get("Date")
            if not date_str:
                continue

            try:
                # 将 yfinance 的 ISO 字符串（带时区）优雅转化为数据库所需的秒级 Unix 整数戳
                dt = datetime.fromisoformat(str(date_str))
                ts = int(dt.timestamp())
            except Exception as e:
                logger.debug(f"Failed to parse datetime string {date_str}: {e}")
                continue

            # 核心防御机制：同时检索标准单索引列名与带 Ticker 后缀的多索引列名
            open_val = row.get("Open") or row.get(f"Open_{symbol_upper}.AX")
            high_val = row.get("High") or row.get(f"High_{symbol_upper}.AX")
            low_val = row.get("Low") or row.get(f"Low_{symbol_upper}.AX")
            close_val = row.get("Close") or row.get(f"Close_{symbol_upper}.AX")
            volume_val = row.get("Volume") or row.get(f"Volume_{symbol_upper}.AX")

            record = {
                "CODE": symbol_upper,
                "RAW_TIMESTAMP": ts,
                "OPEN_PRICE": float(open_val) if open_val is not None else None,
                "HIGH_PRICE": float(high_val) if high_val is not None else None,
                "LOW_PRICE": float(low_val) if low_val is not None else None,
                "CLOSE_PRICE": float(close_val) if close_val is not None else None,
                "VOLUME": float(volume_val) if volume_val is not None else None,
            }

            # 核心质量断言：唯有当关键的价格与量能数据完整有效时，才允许汇入入库缓冲队列
            if record["CLOSE_PRICE"] is not None and record["VOLUME"] is not None:
                records.append(record)

        if records:
            # 合并写入 GoldenWattle Oracle 目标表
            self.db.execute_merge(self.target_table, records, primary_keys=self.primary_keys)
        return records
