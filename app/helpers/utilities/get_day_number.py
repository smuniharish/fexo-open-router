from datetime import datetime


def get_day_number() -> int:
    return datetime.today().weekday() + 1
