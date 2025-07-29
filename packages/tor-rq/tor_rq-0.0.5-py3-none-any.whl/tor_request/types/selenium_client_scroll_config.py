from dataclasses import dataclass


@dataclass(frozen=True)
class SeleniumClientScrollConfig:
    """
    Selenium 기반 클라이언트에서 스크롤 기능에 대한 설정을 정의하는 클래스입니다.

    Attributes:
        scroll (bool): True일 경우 페이지 스크롤을 활성화합니다. False일 경우 정적인 페이지로 간주합니다.
        trial (int): 스크롤 시도 횟수입니다. 페이지 하단까지 스크롤을 몇 번 반복할지 설정합니다.
        delay (int): 각 스크롤 시도 간의 대기 시간(초)입니다.

    Example:
        >>> scroll_config = SeleniumClientScrollConfig(
        ...     scroll=True,
        ...     trial=3,
        ...     delay=2
        ... )
    """

    scroll: bool = True       # 스크롤 수행 여부
    trial: int = 3            # 스크롤 시도 횟수
    delay: int = 3            # 스크롤 간 대기 시간 (초)
