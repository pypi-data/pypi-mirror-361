import socket
from typing import Optional, List, Dict
import logging
import requests
from tor_request.controller.interfaces.abstract_tor_controller import AbstractTorController


class BaseTorController(AbstractTorController):
    """
    TorController의 공통 기능을 제공하는 기본 구현 클래스입니다.

    - 포트 열림 여부 확인
    - 가능한 Tor 포트 목록 스캔
    - 현재 Tor IP 확인 및 로깅

    Subclass에서 IP 갱신 등의 Tor 제어 기능을 확장하거나 재정의할 수 있습니다.
    """

    default_tor_port_sets = [
        {"host": "127.0.0.1", "socks": 9050, "control": 9051},
        {"host": "127.0.0.1", "socks": 9060, "control": 9061},
        {"host": "0.0.0.0", "socks": 9050, "control": 9051},
        {"host": "0.0.0.0", "socks": 9060, "control": 9061},
    ]

    def __init__(self, control_port=9051, log_level: int = logging.INFO):
        """
        BaseTorController 초기화 메서드.

        Args:
            control_port (int): 기본 Tor 제어 포트 (default: 9051)
            log_level (int): 로깅 레벨 (default: logging.INFO)
        """
        super().__init__(log_level=log_level)
        self.control_port = control_port

    def is_port_open(self, host: str, port: int, timeout: int = 5) -> bool:
        """
        특정 호스트:포트 조합에 대해 TCP 연결 가능 여부를 확인합니다.

        Args:
            host (str): 검사할 호스트 (ex. "127.0.0.1")
            port (int): 검사할 포트 번호 (ex. 9051)
            timeout (int): 연결 시도 제한 시간 (초)

        Returns:
            bool: 포트가 열려 있으면 True, 닫혀 있으면 False

        Example:
            is_open = self.is_port_open("127.0.0.1", 9051)
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0

    def scan_possible_tor_ports(
        self,
        port_sets: Optional[List[Dict]] = None,
        timeout: int = 5
    ) -> List[Dict]:
        """
        가능한 SOCKS 및 Control 포트 조합을 순회하며 열린 포트를 탐색합니다.

        Args:
            port_sets (List[Dict]): 검사할 포트 조합 목록 (host/socks/control 키 포함)
            timeout (int): 각 포트에 대한 연결 시도 타임아웃 (초)

        Returns:
            List[Dict]: 포트 조합별 상태 목록
                예: [{'host': '127.0.0.1', 'socks': 9050, 'socks_open': True, ...}]

        Example:
            open_ports = self.scan_possible_tor_ports()
        """
        port_sets = port_sets or self.default_tor_port_sets
        results = [self._check_port_pair(pair, timeout) for pair in port_sets]
        self._log_port_scan_results(results)
        return results


    def _check_port_pair(self, pair: Dict, timeout: int) -> Dict:
        """
        주어진 포트쌍의 SOCKS 및 CONTROL 포트 열림 여부를 확인합니다.

        Args:
            pair (Dict): {'host': str, 'socks': int, 'control': int}
            timeout (int): 연결 시도 시간 제한

        Returns:
            Dict: 검사 결과
        """
        host = pair.get("host", "127.0.0.1")
        socks_port = pair["socks"]
        control_port = pair["control"]

        return {
            "host": host,
            "socks": socks_port,
            "control": control_port,
            "socks_open": self.is_port_open(host, socks_port, timeout),
            "control_open": self.is_port_open(host, control_port, timeout)
        }

    def _log_port_scan_results(self, results: List[Dict]):
        """
        포트 스캔 결과를 보기 좋게 로깅합니다.

        Args:
            results (List[Dict]): 포트 상태 결과 리스트
        """
        self.logger.info("🔍 Tor 포트 스캔 결과:")
        for r in results:
            self.logger.info(
                f"  [{r['host']}] "
                f"SOCKS {r['socks']} - {'✅' if r['socks_open'] else '❌'} | "
                f"CONTROL {r['control']} - {'✅' if r['control_open'] else '❌'}"
            )

    def get_current_ip(
        self,
        proxies: dict = None,
        timeout: int = 30
    ) -> str:
        """
        현재 Tor 네트워크를 통해 사용 중인 IP를 반환합니다.

        - 기본 프록시는 SOCKS5 방식의 127.0.0.1:9050 입니다.
        - ip-api.com/json 응답에서 `query` 키에 있는 IP 주소를 반환합니다.

        Args:
            proxies (dict): requests 전송 시 사용할 Tor 프록시 설정
            timeout (int): 응답 타임아웃 (초)

        Returns:
            str: 현재 Tor IP 주소 (예: "185.220.101.1")

        Raises:
            Exception: 요청 실패 또는 파싱 오류 발생 시 예외 발생

        Example:
            ip = self.get_current_ip()
            print(f"현재 IP는 {ip}입니다.")
        """
        proxies = proxies or self._get_default_proxies

        try:
            response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=timeout)
            ip_info = response.json()
            self._log_ip_info(ip_info)
            return ip_info.get("query")

        except Exception as e:
            self.logger.exception(f"❌ 현재 IP 조회 오류: {e}")
            raise

    @property
    def _get_default_proxies(self) -> dict:
        """
        기본 SOCKS5 프록시 설정을 반환합니다.

        Returns:
            dict: {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
        """
        return {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050"
        }

    def _log_ip_info(self, ip_info: dict):
        """
        IP 정보를 보기 좋은 형식으로 로깅합니다.

        Args:
            ip_info (dict): ip-api.com JSON 응답
        """
        msg = "\n🌍 현재 IP 정보\n" + "\n".join([f"  - {k}={v}" for k, v in ip_info.items()])
        self.logger.info(msg)
