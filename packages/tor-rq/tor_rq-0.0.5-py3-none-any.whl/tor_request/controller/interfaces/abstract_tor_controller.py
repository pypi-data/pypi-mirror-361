from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import logging
from tor_request.utiles.get_logger import get_logger

class AbstractTorController(ABC):
    """
    Tor 제어 인터페이스를 정의하는 추상 클래스.
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        초기화 메서드

        Args:
            log_level (int): 로깅 레벨 (기본값: logging.INFO)
        """
        self.logger = get_logger(name=__name__, level=log_level)

    @abstractmethod
    def renew_ip(self):
        """Tor IP를 갱신합니다."""
        raise NotImplementedError()

    @abstractmethod
    def get_current_ip(self, proxies: Optional[Dict] = None, timeout: int = 30) -> str:
        """현재 사용 중인 Tor IP를 반환합니다."""
        raise NotImplementedError()

    @abstractmethod
    def is_port_open(self, host: str, port: int, timeout: int = 5) -> bool:
        """지정된 포트가 열려 있는지 확인합니다."""
        raise NotImplementedError()

    @abstractmethod
    def scan_possible_tor_ports(self, port_sets: Optional[List[Dict]] = None, timeout: int = 5) -> List[Dict]:
        """가능한 Tor 포트를 스캔하고 결과를 반환합니다."""
        raise NotImplementedError()
