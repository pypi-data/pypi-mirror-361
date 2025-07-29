import logging
import requests

# 커스텀 로깅 유틸리티, 내부적으로 logging.Logger 객체를 반환
from tor_request.utiles.get_logger import get_logger

# Tor 제어용 Base 클래스 (get_current_ip 등 Tor 관련 기능 포함)
from tor_request.base.base_request_client import BaseRequestClient

from tor_request.types.requests_client_config import RequestsClientConfig


class RequestsClient(BaseRequestClient):
    """
    Requests 기반 API 클라이언트 클래스

    - 이 클래스는 Tor 네트워크를 통해 HTTP 요청을 보냅니다.
    - 요청 실패 시, 예외를 발생시켜 retry 로직이 작동할 수 있도록 설계되어 있습니다.

    Example:
        from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

        retry_wrapper = retry(
            stop=stop_after_attempt(5),
            wait=wait_fixed(2),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )

        client = RequestsClient()
        response = client.request_with_retry("http://httpbin.org/ip", retry_func=retry_wrapper)
        print(response.text)
    """

    def __init__(self, config: RequestsClientConfig = RequestsClientConfig()):
        """
        객체 초기화 메서드

        Args:
            config (RequestsClientConfig): 요청 동작을 제어할 설정 객체
            logger (logging.Logger): 로깅 객체
        """
        # BaseRequestClient(Tor 관련) 초기화
        super().__init__(log_level=config.log_level, control_port=config.control_port)
        self.config = config

    def perform_request(self, url: str, method: str = "get", **kwargs):
        """
        Tor 네트워크를 통해 HTTP 요청을 수행하는 메서드

        - 요청 실패 시 `response.raise_for_status()`로 예외를 유도하여 retry 유도
        - 메서드 이름은 request_with_retry 내부에서 호출됨

        Args:
            url (str): 요청할 URL
            method (str): HTTP 메서드 (GET, POST, PUT 등)
            **kwargs: headers, params, timeout 등 requests 인자

        Returns:
            requests.Response: 요청에 대한 응답 객체

        Raises:
            requests.exceptions.RequestException: 요청 실패 시
        """

        self._log_request(url, method, kwargs)

        # 동적 메서드 가져오기 (requests.get, requests.post 등)
        request_func = self._get_request_func(method)

        # timeout이 없으면 30초 기본값 설정
        kwargs = self._set_default_timeout(kwargs)

        # 요청 실행 (proxies는 Tor 프록시 주소 사용)
        response = request_func(url=url, proxies=self.config.proxies, **kwargs)

        # 응답 상태 코드 확인 (2xx 외는 raise)
        response.raise_for_status()

        return response

    def _log_request(self, url: str, method: str, kwargs: dict):
        """
        요청 정보를 로그로 출력하는 함수

        Args:
            url (str): 요청 URL
            method (str): HTTP 메서드
            kwargs (dict): 요청 파라미터 및 헤더 정보

        Example:
            [REQUEST] Method: [get] | url: http://ip-api.com/json
            [REQUEST PARAMS] {'query': 'KOR'}
        """

        self.logger.info(f"[REQUEST] Method: [{method}] | url: {url}")
        if "params" in kwargs:
            self.logger.debug(f"[REQUEST PARAMS] {kwargs['params']}")
        if "headers" in kwargs:
            self.logger.debug(f"[REQUEST HEADERS] {kwargs['headers']}")

    def _get_request_func(self, method: str):
        """
        HTTP 메서드에 해당하는 requests 함수 반환

        Args:
            method (str): "get", "post" 등

        Returns:
            Callable: requests.get, requests.post 등

        Raises:
            ValueError: 존재하지 않는 메서드인 경우
        """
        try:
            return getattr(requests, method)
        except AttributeError:
            raise ValueError(f"[ERROR] 지원하지 않는 HTTP 메서드: {method}")

    def _set_default_timeout(self, kwargs: dict) -> dict:
        """
        timeout 기본값 설정 (없으면 30초로 설정)

        Args:
            kwargs (dict): 기존 인자들

        Returns:
            dict: timeout이 보장된 kwargs
        """
        kwargs = kwargs.copy()
        kwargs.setdefault("timeout", 30)
        return kwargs


# ===============================
# ✅ 테스트 및 예제 실행 영역
# ===============================
if __name__ == "__main__":
    config = RequestsClientConfig()
    client = RequestsClient(config=config)

    url = "http://ip-api.com/json"

    try:
        # 현재 IP (Tor 프록시 뒤의 실제 IP) 출력
        client.tor.get_current_ip()
        print()

        # GET 요청 테스트
        response = client.request_with_retry(url=url)
        print("Response:", response.text)
        print("Current IP:", response.json().get("query"))

        print()
        client.tor.get_current_ip()
        print()

        # POST 요청 테스트
        response = client.request_with_retry(url=url, method="post")
        print("Response:", response.text)
        print("Current IP:", response.json().get("query"))
    except Exception as e:
        print("Error:", e)


    # ==========================
    # 🔁 Retry 데코레이터 테스트
    # ==========================
    print("🔁 재시도 테스트 시작")

    from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
    from tenacity import before_sleep_log, after_log

    # 로깅 객체 생성
    after_logger = get_logger("[After] 재시도 테스트", logging.INFO)
    before_logger = get_logger("[Before] 재시도 테스트", logging.INFO)

    # Retry 래퍼 정의: 실패 시 최대 4번까지 3초 간격 재시도
    custom_retry = retry(
        stop=stop_after_attempt(4),
        wait=wait_fixed(3),
        retry=retry_if_exception_type(Exception),
        reraise=True,
        before_sleep=before_sleep_log(after_logger, logging.INFO),
        after=after_log(before_logger, logging.INFO)
    )

    # 일부러 실패하게 만들 URL
    url = "http://this-url-does-not-exist.tld"

    if __name__ == "__main__":
        config = RequestsClientConfig()
        client = RequestsClient(config=config)

        try:
            print("🔁 재시도 테스트 시작")
            # retry 데코레이터를 통해 실패한 경우 자동 재시도
            response = client.request_with_retry(url=url, retry_func=custom_retry)
            print("✅ 요청 성공:", response.text)
        except Exception as e:
            print("❌ 요청 최종 실패:", e)
