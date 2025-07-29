from abc import ABC, abstractmethod
from typing import Optional, Callable
import logging

from tor_request.utiles.get_logger import get_logger


class AbstractRequestClient(ABC):
    """
    RequestClient의 추상 기반 클래스.

    - 외부 HTTP 요청을 처리하는 클라이언트의 공통 인터페이스 정의
    - request 수행 방식은 `perform_request` 메서드를 통해 하위 클래스에서 구현
    - 재시도 로직이 포함된 요청 메서드는 `request_with_retry`로 구현을 위임
    - 로깅 기능 포함 (레벨 지정 가능)

    이 클래스를 상속받는 모든 클라이언트는 `perform_request`와 `request_with_retry`
    메서드를 반드시 구현해야 합니다.
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        AbstractRequestClient 초기화 메서드

        Args:
            log_level (int): 로깅 레벨 (기본값: logging.INFO)
                - logging.DEBUG: 상세 디버깅 정보 출력
                - logging.INFO: 일반 정보 출력
                - logging.WARNING: 경고 메시지 출력
                - logging.ERROR: 에러 메시지 출력

        Example:
            client = MyRequestClient(log_level=logging.DEBUG)
        """
        self.logger = get_logger(name=__name__, level=log_level)

    @abstractmethod
    def perform_request(self, *args, **kwargs):
        """
        실제 HTTP 요청을 수행하는 추상 메서드.

        하위 클래스에서 이 메서드를 구현하여 HTTP 요청 (GET, POST 등)을 처리해야 합니다.

        Args:
            *args: 위치 인자 (예: URL, 파라미터 등)
            **kwargs: 키워드 인자 (예: headers, payload 등)

        Returns:
            Any: 요청 결과 (예: 응답 객체, JSON 데이터 등)

        Raises:
            Exception: 요청 수행 중 발생 가능한 예외를 그대로 전달하거나 처리
        """
        raise NotImplementedError("perform_request 메서드는 반드시 하위 클래스에서 구현해야 합니다.")

    @abstractmethod
    def request_with_retry(
        self,
        *args,
        retry_func: Optional[Callable[[Callable], Callable]] = None,
        **kwargs
    ):
        """
        재시도 로직이 포함된 요청 메서드.

        기본적으로 `tenacity.retry`와 같은 데코레이터 함수로 재시도 정책을 주입받아 사용합니다.
        요청 실패 시 주어진 재시도 조건에 따라 perform_request를 자동으로 재시도합니다.

        Args:
            retry_func (Optional[Callable]): 재시도 데코레이터 함수 (tenacity.retry 등).
                None인 경우, 하위 클래스에서 기본 재시도 정책을 정의해야 합니다.
            *args: perform_request에 전달할 위치 인자
            **kwargs: perform_request에 전달할 키워드 인자

        Returns:
            Any: 요청 성공 시의 응답 결과

        Raises:
            Exception: 최대 재시도 횟수를 초과하거나 예외 발생 시 예외를 발생시킵니다.
        """
        raise NotImplementedError("request_with_retry 메서드는 반드시 하위 클래스에서 구현해야 합니다.")
