import time


def milliseconds_time_now() -> int:
    return int(time.time() * 1000)


def date_seconds_diff_to_now(date_in_milliseconds: int) -> int:
    # Diff in milliseconds, divide by 1000 to convert to seconds.
    return (milliseconds_time_now() - date_in_milliseconds) // 1000

