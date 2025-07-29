import logging
import time
from abc import abstractmethod

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    after_log
)

from typing import Optional, Callable

from tor_request.utiles.format_elapsed_time import format_elapsed_time
from tor_request.controller.tor_control import TorController
import json
from tor_request.interfaces.abstract_request_client import AbstractRequestClient

class BaseRequestClient(AbstractRequestClient):
    """API 요청을 수행하는 추상 클래스

    Example:
        1. perform_request를 구현하고.
        2. 실행은 request_with_retry를 하여 자동 재시도 및 IP 갱신을 수행합니다.

    - Tor 네트워크를 통한 요청을 수행
    - 요청 실패 시 Tor IP를 갱신하고 재시도
    - 자식 클래스는 perform_request 메서드를 구현해야 함
    """

    def __init__(self, log_level: int= logging.INFO, control_port=9051):
        """
        초기화 메서드

        Args:
            max_retries (int): 최대 재시도 횟수 (기본값: 3)
        """
        super().__init__(log_level=log_level)
        # Tor IP 제어를 위한 컨트롤러 인스턴스
        self.tor = TorController(control_port=control_port)  

    @abstractmethod
    def perform_request(self, *args, **kwargs):
        """
        실제 요청을 수행하는 메서드 (자식 클래스에서 반드시 구현 필요)

        Returns:
            요청 결과 (예: HTML, JSON 등)
        """
        raise NotImplementedError("perform_request 메서드는 자식 클래스에서 구현해야 합니다.")

    def _log_response_info(self, res):
        """
        응답 객체의 주요 정보 로깅 메서드

        - 객체 타입
        - 상태 코드, 헤더
        - 본문 미리보기 (JSON or Text)
        - 응답 파싱 오류 처리 포함
        """
        self._log_response_type(res)
        self._log_status_and_headers(res)
        self._log_body_preview(res)

    def _log_response_type(self, res):
        """응답 객체의 클래스 타입 로그 출력"""
        self.logger.info(f"🔎 Response 객체 타입: {type(res)}")

    def _log_status_and_headers(self, res):
        """상태 코드 및 응답 헤더 출력"""
        status_code = getattr(res, "status_code", None)
        headers = getattr(res, "headers", None)

        self.logger.info(f"📦 Status Code: {status_code}")
        self.logger.info(f"📬 Res Headers: {headers}")

        # 추가 정보 예시: 요청 URL (가능한 경우)
        url = getattr(res, "url", None)
        if url:
            self.logger.info(f"🔗 Request URL: {url}")

        # 응답 시간 (가능한 경우)
        elapsed = getattr(res, "elapsed", None)
        if elapsed:
            self.logger.info(f"⏱️ 응답 시간: {elapsed.total_seconds():.2f}s")

    def _log_body_preview(self, res):
        """응답 본문 미리보기 (JSON or TEXT)"""
        try:
            if hasattr(res, "json"):
                body = res.json()
                json_str = json.dumps(body, indent=2, ensure_ascii=False)
                preview = json_str[:100].strip() + ("..." if len(json_str) > 100 else "")
                self.logger.info(f"🧾 JSON Body Preview:\n{preview}")

            else:
                text_preview = getattr(res, "text", None)
                if text_preview:
                    self.logger.info(f"🧾 Response Text (preview): {text_preview[:100]}")
                else:
                    self.logger.info("🧾 Response Text 없음")
        except Exception as e:
            self.logger.warning(f"⚠️ 응답 본문 json 파싱 실패: {e}")

    def _handle_exception(self, e: Exception):
        """
        예외 처리 및 Tor IP 갱신
        """
        self.logger.error(f"❌ 요청 실패: {e}")
        self.logger.info("🔄 Tor IP 갱신 후 재시도 중...")
        self.tor.renew_ip()

    def request_with_retry(
            self,
            *args,
            retry_func: Optional[Callable[[Callable], Callable]] = None,
            **kwargs
    ):
        """
        외부에서 전달받은 retry 데코레이터를 사용하여 요청을 수행하고,
        실패 시 Tor IP를 갱신하여 재시도.

        Example:
            from tenacity import stop_after_attempt, wait_fixed, retry_if_exception_type, retry

            # 사용자 정의 리트라이 조건
            custom_retry = retry(
                stop=stop_after_attempt(5),
                wait=wait_fixed(3),
                retry=retry_if_exception_type(Exception),
                reraise=True
            )

            client.request_with_retry(retry_func=custom_retry)

        Args:
            retry_func: tenacity.retry(...) 형태의 데코레이터 함수
            args/kwargs: 요청에 필요한 인자

        Returns:
            Any: 요청 결과

        """

        retry_func = retry_func or retry(  # 기본 리트라이 조건
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=4, min=10, max=60),
            retry=retry_if_exception_type(Exception),
            after=after_log(self.logger, logging.DEBUG),
            reraise=True
        )

        @retry_func
        def _do_request_with_retry():
            self.logger.info("🟢 요청을 시작합니다.")

            start = time.time()
            try:
                res = self.perform_request(*args, **kwargs)
                self.logger.info(f"✅ 요청 성공 | 소요 시간: {format_elapsed_time(time.time() - start)}")
                self._log_response_info(res)

                return res
            except Exception as e:
                self._handle_exception(e)
                raise

        return _do_request_with_retry()
