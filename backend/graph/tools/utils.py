from datetime import datetime, timedelta


def _parse_date(date_str: str | None, default_days_ago: int = 0) -> str:
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
    return (datetime.now().date() - timedelta(days=default_days_ago)).isoformat()
