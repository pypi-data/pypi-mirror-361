import logging
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestsClientConfig:
    """
    Requests 기반 클라이언트 요청을 구성하기 위한 설정값들을 저장하는 데이터 클래스입니다.

    이 클래스는 Tor 네트워크를 이용한 HTTP 요청 환경을 설정하는 데 사용되며,
    로깅 수준, 프록시 설정, 제어 포트 등의 다양한 설정값을 캡슐화합니다.

    Attributes:
        log_level (int): 로깅 레벨 (예: logging.INFO, logging.DEBUG 등).
                         로깅 출력의 상세 정도를 제어합니다.
        control_port (int): Tor 제어 포트 번호 (기본값: 9051).
                            TorController와 통신하기 위한 포트입니다.
        proxies (dict): HTTP 및 HTTPS 요청에 사용할 프록시 설정.
                        기본적으로 Tor 네트워크를 통해 요청하기 위한 SOCKS5 주소가 설정됩니다.

    Example:
        >>> config = RequestsClientConfig(
        ...     log_level=logging.DEBUG,
        ...     control_port=9061,
        ...     proxies={
        ...         "http": "socks5://127.0.0.1:9060",
        ...         "https": "socks5://127.0.0.1:9060"
        ...     }
        ... )
    """

    log_level: int = logging.INFO  # 로깅 수준 (예: DEBUG, INFO, WARNING 등)

    control_port: int = 9051  # Tor 네트워크의 제어 포트 (기본: 9051)

    proxies: dict = field(
        default_factory=lambda: {
            "http": "socks5://127.0.0.1:9050",
            "https": "socks5://127.0.0.1:9050"
        }
    )
    # HTTP/HTTPS 요청 시 사용할 프록시 설정
    # 기본값은 로컬호스트의 Tor SOCKS5 프록시 포트 (9050)을 사용
