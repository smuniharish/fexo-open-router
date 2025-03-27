from datetime import datetime


def get_current_time() -> int:
    return int(datetime.now().strftime("%H%M"))
