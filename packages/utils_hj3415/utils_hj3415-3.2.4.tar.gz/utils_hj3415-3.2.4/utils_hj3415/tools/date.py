import datetime
import re
from typing import Optional

def str_to_date(date_str: str) -> datetime.datetime:
    """
    Convert a string representation of a date into a datetime object by trying
    multiple common date formats until successful. If no format matches, it raises
    a ValueError.

    # 변환가능한 형식

    '2021년 04월 13일'

    '2021/04/13'

    '2021-04-13'

    '2021.04.13'

    '20210413'


    Parameters:
        date_str (str): The date string to be converted.

    Returns:
        datetime: A datetime object corresponding to the parsed date.

    Raises:
        ValueError: If the input string cannot be parsed into a valid datetime
        object using any of the predefined formats.
    """
    # 대안 - dateutil.parser(서드파티 라이브러리)를 쓰면 다양한 패턴을 자동 인식합니다.
    d_clean = date_str.replace(" ", "")

    formats = [
        "%Y년%m월%d일",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y%m%d"
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(d_clean, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date type - {date_str}")

def date_to_str(d: datetime.datetime, sep: Optional[str] = '-') -> str:
    """
    Convert a datetime object to its string representation.

    This function converts a datetime object to a string with a given
    separator. If no separator is provided, the default separator ('-')
    will be used. If the separator is explicitly set to `None`, the
    date will be formatted without any separator.

    # 사용 예시\n
    dt = datetime.datetime(2021, 4, 13)\n
    print(date_to_str(dt))         # "2021-04-13"\n
    print(date_to_str(dt, '/'))    # "2021/04/13"\n
    print(date_to_str(dt, None))   # "20210413"\n

    Arguments:
        d: datetime
            The datetime object to be converted.
        sep: str, optional
            The separator to use in the date string. Defaults to '-'.
            If set to None, the output will not include any separator.

    Returns:
        str
            The string representation of the given datetime object in the
            specified format.
    """
    if sep is None:
        return d.strftime('%Y%m%d')
    else:
        return d.strftime(f"%Y{sep}%m{sep}%d")

def isYmd(date: str) -> bool:
    """
    날짜 문자열이 YYYYMMDD 형식이고 유효한 날짜인지 확인.

    # 예시

    print(isYmd("20101120"))  # True

    print(isYmd("20200229"))  # True (윤년)

    print(isYmd("20211301"))  # False (잘못된 월)

    print(isYmd("2010.11.20"))  # False (잘못된 형식)

    print(isYmd("20210230"))  # False (잘못된 일)

    Args:
        date (str): 날짜 문자열.

    Returns:
        bool: 유효한 형식이면 True, 그렇지 않으면 False.
    """
    # 기본 정규식 확인
    if not re.match(r'^20\d{6}$', date):
        return False

    # 날짜 유효성 확인
    try:
        datetime.datetime.strptime(date, "%Y%m%d")
        return True
    except ValueError:
        return False

def isY_slash_m(date: str) -> bool:
    """
    date 인자의 형식이 Y/m (YYYY/MM) 인지 확인.

    Args:
        date (str): 날짜 형태의 문자열

    Returns:
        bool: True면 Y/m 형식, False면 다른 형식
    """
    return bool(re.match(r'^20\d{2}/(0[1-9]|1[0-2])$', date))

def is_within_last_n_days(date_to_check: datetime.datetime.date, timedelta_days=3) -> bool:
    """
    Determines if a given date is within the last N days.

    This function checks whether a specific date is between today and the specified number
    of days ago. It is useful for verifying if a date falls within a recent period.

    Args:
        date_to_check (datetime.datetime.date): The date to evaluate.
        timedelta_days (int, optional): The number of days to look back from today.
            Defaults to 3.

    Returns:
        bool: True if the date falls within the range from today to N days ago,
        inclusive; False otherwise.
    """
    if isinstance(date_to_check, datetime.datetime):
        date_to_check = date_to_check.date()  # datetime.date로 변환
    elif isinstance(date_to_check, datetime.date):
        date_to_check = date_to_check  # 이미 datetime.date인 경우 그대로 반환
    else:
        raise TypeError("Input is not a datetime.datetime or datetime.date object")

    today = datetime.datetime.now().date()  # 현재 날짜 (시간은 무시)
    # print('today - ', today)
    n_days_ago = today - datetime.timedelta(days=timedelta_days)
    return n_days_ago <= date_to_check <= today