from datetime import datetime
import config


def ts_to_date_str(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def in_date_range(ts: int) -> bool:
    date_str = ts_to_date_str(ts)
    return config.DATE_START <= date_str <= config.DATE_END
