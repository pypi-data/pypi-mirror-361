from dataclasses import dataclass
import logging

@dataclass(frozen=True)
class SeleniumClientConfig:
    """
    Selenium 기반 클라이언트에서 사용할 구성 설정 클래스입니다.
    Tor 네트워크를 활용한 프록시 설정 및 기타 옵션들을 관리합니다.

    Attributes:
        log_level (int): True일 경우 디버깅 및 로깅을 활성화합니다. 기본값은 True입니다.
        control_port (int): Tor 제어 포트 번호입니다. 기본값은 9051입니다.
        is_no_ssl (bool): HTTPS 인증서 오류 무시 여부. True이면 SSL 인증서 무시. 디버깅용.
        proxy_server (str): Selenium이 사용할 프록시 서버 주소입니다. 기본값은 socks5 방식의 로컬 Tor 프록시입니다.

    Example:
        >>> config = SeleniumClientConfig(
        ...     verbose=True,
        ...     control_port=9051,
        ...     is_no_ssl=True,
        ...     proxy_server="socks5://127.0.0.1:9050"
        ... )
    """

    log_level: int = logging.INFO  # 디버깅 및 로깅 활성화 여부
    control_port: int = 9051  # Tor 네트워크의 제어 포트 번호
    is_no_ssl: bool = False  # SSL 인증서 무시 여부 (비추천, 디버깅용)
    proxy_server: str = "socks5://127.0.0.1:9050"  # 사용할 프록시 서버 주소