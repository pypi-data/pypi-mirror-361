import math
import re
from typing import Optional
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'INFO')

def parse_won(text: str) -> int:
    """
    한국 화폐 표현 문자열을 숫자로 변환 (조원, 억원, 만원, 원, 억 등 처리)
    """
    units = {
        "조원": 1_000_000_000_000,
        "억원": 100_000_000,
        "억":   100_000_000,
        "만원": 10_000,
        "원": 1,
    }

    text = text.replace(",", "").strip()
    match = re.match(r"([-+]?[0-9]*\.?[0-9]+)([가-힣]+)", text)

    if not match:
        raise ValueError(f"형식이 잘못된 금액 문자열: {text}")

    number, unit = match.groups()
    if unit not in units:
        raise ValueError(f"알 수 없는 단위: {unit}")

    return int(float(number) * units[unit])

def format_large_number(number:int) -> str:
    """
    Formats a large integer into a Korean-style segmented number with units.

    This function takes an integer number and formats it by separating it into segments
    of Korean numbering units such as '조', '억', and '만'. For each unit, the appropriate
    quotient is calculated and appended to the result. Any remainder less than 10,000
    is included at the end. The formatted result is returned as a string.

    Parameters:
    number (int): The large integer to format.

    Returns:
    str: The formatted number as a string with Korean numbering units.
    """
    # 숫자를 분해할 단위와 이름
    units = [("조", 10 ** 12), ("억", 10 ** 8), ("만", 10 ** 4)]
    result = []

    # 숫자를 처리
    for unit_name, unit_value in units:
        if number >= unit_value:
            quotient, number = divmod(number, unit_value)
            if quotient > 0:
                result.append(f"{quotient}{unit_name}")

    # 남은 숫자가 있으면 포함
    if number > 0:
        result.append(str(number))

    return " ".join(result)

def format_with_commas(number) -> str:
    """
    숫자를 입력받아 천단위로 콤마를 붙인 문자열로 반환하는 함수.
    :param number: 숫자(int 또는 float)
    :return: 천단위 콤마가 포함된 문자열
    """
    try:
        # 정수형인지 실수형인지 확인하여 포맷팅
        if isinstance(number, int):
            return f"{number:,}"
        elif isinstance(number, float):
            return f"{number:,.2f}"  # 소수점 이하 2자리까지
        else:
            raise ValueError("숫자 타입이 아닙니다.")
    except ValueError as e:
        return f"오류: {e}"

def to_int(value) -> int:
    """
    Converts the input value to an integer. This function first converts the input value
    to a float, replaces NaN with zero, and then converts the result to an integer.

    Args:
        value: The input value to be converted, which can be of any data type that can be
               parsed as a float.

    Returns:
        int: The integer representation of the input value, with NaN values replaced by zero.
    """
    return int(nan_to_zero(to_float(value)))

def to_float(value, nan_to_none=False) -> Optional[float]:
    """
    주어진 값을 float 형식으로 변환합니다. 문자열, 정수, 부동소수점, 그리고 회계식 음수 표기 등을 처리하며,
    변환이 불가능한 경우 `NaN` 또는 `None`을 반환할 수 있습니다.

    Args:
        value (Any): 변환하려는 값. 정수(int), 부동소수점(float), 문자열(str) 형식을 지원합니다.
                     문자열은 회계식 음수 표기(예: "(123.45)")와 쉼표(,) 또는 퍼센트(%) 기호를 제거하여 처리합니다.
        nan_to_none (bool, optional): 변환이 불가능할 때 반환 값을 설정합니다.
                                      True일 경우 `None` 반환, False일 경우 `NaN` 반환. 기본값은 False입니다.

    Returns:
        Optional[float]: 변환된 부동소수점 값. 변환이 불가능하면 `NaN` 또는 `None`을 반환합니다.

    Examples:
        >>> to_float("123.45")
        123.45

        >>> to_float("(123.45)")
        -123.45

        >>> to_float("1,234.56")
        1234.56

        >>> to_float("50%")
        50.0

        >>> to_float("abc", nan_to_none=True)
        None

        >>> to_float("abc", nan_to_none=False)
        nan

        >>> to_float(123)
        123.0
    """
    mylogger.debug(f"to_float : {value}")

    # 1) 이미 숫자형(int, float)이면 바로 float 변환
    if isinstance(value, (int, float)):
        return float(value)

    try:
        # 2) 문자열 전처리
        s = str(value).strip()

        # 2-1) 회계식 음수 표기 여부 확인: (....)
        negative = False
        if s.startswith('(') and s.endswith(')'):
            negative = True
            # 괄호 제거
            s = s[1:-1]

        # 2-2) 쉼표와 퍼센트 기호 제거
        s = s.replace(',', '').replace('%', '')

        # 3) float 변환
        result = float(s)

        # 4) 회계식 음수였으면 부호 반전
        if negative:
            result = -result

        return result

    except (ValueError, TypeError):
        # 변환 불가능하면 NaN 반환
        if nan_to_none:
            return None
        else:
            return float('nan')

def nan_to_zero(value) -> float:
    """
    Convert input value to float, replacing NaN, infinity, or None with zero.

    This function ensures that invalid or non-numeric inputs like NaN, infinity, or
    None are safely converted to zero. The input is first converted to a float, and
    then checked for its validity. If the value is not a number or is not finite,
    it is replaced with 0.0.

    Parameters:
        value: Any
            Input value to be converted to a valid float.

    Returns:
        float
            A valid floating-point number, or 0.0 if the input is invalid, NaN,
            infinity, or None.
    """
    if value is None:
        return 0.0
    f_value = to_float(value)
    return 0.0 if math.isnan(f_value) or math.isinf(f_value) else f_value

def is_6digit(s: str) -> bool:
    """
    파일명이 숫자 6자리인지 검사하여 반환.
    """
    return s.isdigit() and len(s) == 6

def replace_nan_to_none(data):
    """ float의 NaN을 None으로 바꿔주고, dict나 list는 재귀적으로 처리한다 """
    if isinstance(data, float):
        return None if math.isnan(data) else data
    elif isinstance(data, dict):
        return {k: replace_nan_to_none(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_nan_to_none(item) for item in data]
    else:
        return data