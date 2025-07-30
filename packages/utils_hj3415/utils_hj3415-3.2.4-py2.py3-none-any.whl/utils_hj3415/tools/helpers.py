import pprint
import random

def pprint_limited_dict(data, limit=10):
    """
    딕셔너리를 예쁘게 출력하되, 리스트/튜플/세트 타입의 값은 최대 `limit` 개까지만 표시합니다.

    매개변수:
        data (dict): 출력할 딕셔너리.
        limit (int, optional): 리스트, 튜플, 세트의 경우 최대 출력할 항목 개수. 기본값은 10.

    반환값:
        None: `pprint.pprint()`를 사용하여 결과를 직접 출력합니다.

    예제:
        >>> sample_data = {
        ...     "numbers": list(range(20)),
        ...     "name": "Alice",
        ...     "scores": (95, 88, 92, 76, 89, 100),
        ...     "tags": {"AI", "ML", "Data Science"},
        ... }
        >>> pprint_limited_dict(sample_data, limit=3)
        {'numbers': [0, 1, 2],
         'name': 'Alice',
         'scores': [95, 88, 92],
         'tags': ['AI', 'Data Science', 'ML']}
    """
    trimmed_data = {}
    for key, value in data.items():
        if isinstance(value, (list, tuple, set)):  # 리스트, 튜플, 세트일 경우
            trimmed_data[key] = list(value)[:limit]  # 최대 10개까지만 출력
        else:
            trimmed_data[key] = value  # 다른 타입은 그대로 유지

    pprint.pprint(trimmed_data)

COMMON_USER_AGENTS = [
    # --- Chrome (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.100 Safari/537.36",

    # --- Chrome (Mac) ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/111.0.5563.64 Safari/537.36",

    # --- Firefox (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) "
    "Gecko/20100101 Firefox/108.0",

    # --- Firefox (Linux) ---
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
    "Gecko/20100101 Firefox/109.0",

    # --- Edge (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.100 Safari/537.36 "
    "Edg/110.0.1587.49",

    # --- Safari (Mac) ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.1 Safari/605.1.15",

    # --- Safari (iPhone iOS) ---
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.0 Mobile/15E148 Safari/604.1",

    # --- Chrome (Android) ---
    "Mozilla/5.0 (Linux; Android 13; SM-S908N) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.65 Mobile Safari/537.36",

    # --- Opera (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.5481.77 Safari/537.36 OPR/96.0.4693.80",

    # --- Older Edge (Windows) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/92.0.902.62 Safari/537.36 "
    "Edg/92.0.902.62",
]

def get_random_user_agent() -> str:
    """랜덤 User-Agent 하나 반환"""
    return random.choice(COMMON_USER_AGENTS)