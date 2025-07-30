import platform
import urllib.request
import socket
from multiprocessing import cpu_count
from typing import List, Tuple
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'INFO')


def get_ip_addr(ipv6: bool = False) -> str:
    """
    현재 시스템의 IP 주소를 반환.
    :param ipv6: True면 IPv6 주소를 반환. 기본은 IPv4.
    """
    family = socket.AF_INET6 if ipv6 else socket.AF_INET
    try:
        with socket.socket(family, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except (socket.error, OSError) as e:
        print(f"Error getting IP address: {e}")
        return "::1" if ipv6 else "0.0.0.0"


def get_external_ip() -> str:
    """
    외부 IP 주소를 반환. 실패 시 "0.0.0.0" 반환.
    """
    try:
        with urllib.request.urlopen("https://api.ipify.org") as response:
            return response.read().decode("utf-8")
    except Exception:
        return "0.0.0.0"

def get_pc_info() -> dict:
    """
    현재 PC의 정보를 반환.
    """
    # 플랫폼 정보 가져오기
    platform_system = platform.system()
    platform_release = platform.release()
    platform_version = platform.version()
    platform_architecture = platform.architecture()[0]

    # 네트워크 정보
    internal_ip = get_ip_addr()
    external_ip = get_external_ip()
    hostname = socket.gethostname()

    return {
        "os": platform_system,
        "version": platform_release,
        "architecture": platform_architecture,
        "internal_ip": internal_ip,
        "external_ip": external_ip,
        "hostname": hostname,
    }

def code_divider_by_cpu_core(entire_codes: list) -> Tuple[int, List[list]]:
    """
    전체 종목 코드를 리스트로 넣으면 CPU 코어 수에 맞춰 리스트를 나누어 준다.

    Args:
        entire_codes (list): 분할할 종목 코드 리스트.

    Returns:
        tuple:
            - n (int): 분할된 파트(코어) 개수
            - divided_list (List[list]): 종목 코드가 분할된 2차원 리스트
    """

    def split_into_parts(alist: list, parts: int) -> List[list]:
        """
        리스트 alist를 parts만큼 대략 균등하게 분할한다.
        """
        length = len(alist)
        return [
            alist[i * length // parts: (i + 1) * length // parts]
            for i in range(parts)
        ]
    core = cpu_count()
    mylogger.info(f"CPU Count: {core}")

    # 최소 코어 수가 1이 되도록
    n = max(core - 1, 1)

    # 코드 수가 파트 수보다 적으면 파트를 코드 수(또는 1)로
    if len(entire_codes) < n:
        n = len(entire_codes) or 1

    mylogger.info(f"Splitting {len(entire_codes)} codes into {n} parts...")
    divided_list = split_into_parts(entire_codes, n)

    return n, divided_list
