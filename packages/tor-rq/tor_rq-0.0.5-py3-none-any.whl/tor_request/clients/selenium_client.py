import logging
import time
import warnings
from urllib.parse import quote

import ssl
import urllib.request
import certifi
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tenacity import (after_log, before_sleep_log, retry,
                      retry_if_exception_type, stop_after_attempt, wait_exponential)

from tor_request.utiles.get_logger import get_logger
from tor_request.base.base_request_client import BaseRequestClient
from tor_request.types.selenium_client_config import SeleniumClientConfig

from tor_request.types.selenium_client_scroll_config import SeleniumClientScrollConfig
from tor_request.utiles.chrome_driver_manager import ChromeDriverManager
from typing import Callable, Any

class SeleniumClient(BaseRequestClient):
    """
    Selenium 기반 웹 크롤러 클라이언트 클래스

    - 웹 드라이버를 초기화하고 관리합니다.
    - 지정한 URL에 접속하여, 필요 시 스크롤을 자동으로 내려 페이지 내 모든 콘텐츠를 가져옵니다.
    - 재시도(retry) 로직을 내장하여, WebDriverException 또는 TimeoutException 발생 시 자동 재시도합니다.
    - 외부에서 재시도 조건을 주입할 수도 있습니다.
    """

    def __init__(self, config: SeleniumClientConfig = SeleniumClientConfig()):
        """
        SeleniumClient 초기화 메서드

        Args:
            config (SeleniumClientConfig, optional): Selenium 동작 관련 설정 객체.
                기본값은 SeleniumClientConfig()의 기본 설정을 사용.
        """
        super().__init__(log_level=config.log_level, control_port=config.control_port)
        self.config = config
        self.driver = None  # 웹 드라이버 초기화

    def _create_ssl_context(self):
        """
        certifi에서 제공하는 신뢰 가능한 인증서를 사용하여 SSL context 생성

        Returns:
            ssl.SSLContext: 설정된 SSL context 객체

        Example:
            >>> ctx = self._create_ssl_context()
        """
        return ssl.create_default_context(cafile=certifi.where())

    def _apply_ssl_context(self, ssl_context):
        """
        urllib의 기본 HTTPS context를 설정하여 SSL 인증서 오류 방지

        Args:
            ssl_context (ssl.SSLContext): 사용할 SSL context 객체

        Example:
            >>> ctx = self._create_ssl_context()
            >>> self._apply_ssl_context(ctx)
        """
        ssl._create_default_https_context = lambda: ssl_context

    def _test_ssl_connection(self, ssl_context):
        """
        SSL context 설정 후 테스트용 HTTPS 요청을 보내 연결 확인 (오류는 무시)

        Args:
            ssl_context (ssl.SSLContext): 사용할 SSL context 객체

        Example:
            >>> ctx = self._create_ssl_context()
            >>> self._test_ssl_connection(ctx)
        """
        try:
            urllib.request.urlopen("https://google.com", context=ssl_context)
        except Exception:
            pass

    def _setup_ssl_context(self):
        """
        SSL 인증서 문제 방지용 SSL context 설정 및 테스트

        Example:
            >>> self._setup_ssl_context()
        """
        ctx = self._create_ssl_context()
        self._apply_ssl_context(ctx)
        self._test_ssl_connection(ctx)

    def _build_chrome_options(self):
        """
        Chrome WebDriver용 옵션 객체를 생성하고 필요한 옵션들을 추가

        Returns:
            selenium.webdriver.chrome.options.Options: 설정된 옵션 객체

        Example:
            >>> options = self._build_chrome_options()
        """
        options = Options()
        options_list = [
            "--headless",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "user-agent=Mozilla/5.0",
            "--disable-blink-features=AutomationControlled",
            "--incognito",
            "--lang=ko_KR",
            "--window-size=2160,3840",
            "--mute-audio",
            f"--proxy-server={self.config.proxy_server}",
            "--enable-logging",
            "--v=1",
        ]
        for option in options_list:
            options.add_argument(option)
        return options

    def _initialize_driver(self):
        """
        ChromeDriverManager에서 드라이버 경로를 받아 Chrome WebDriver 객체를 생성

        Returns:
            selenium.webdriver.Chrome: 초기화된 WebDriver 객체

        Example:
            >>> driver = self._initialize_driver()
        """
        options = self._build_chrome_options()
        exe_path = ChromeDriverManager.drvier_install_with_path()
        service = Service(executable_path=exe_path, verbose=True)
        return webdriver.Chrome(options=options, service=service)

    def _is_driver_alive(self):
        """
        현재 Selenium WebDriver가 정상 작동하는지 확인

        Returns:
            bool: 드라이버가 정상 작동 중이면 True, 그렇지 않으면 False

        Example:
            >>> alive = self._is_driver_alive()
        """
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                _ = self.driver.title
            return True
        except Exception:
            return False

    def _ensure_driver(self):
        """
        드라이버가 없거나 비정상 상태인 경우 새로 초기화

        Example:
            >>> self._ensure_driver()
        """
        if self.driver is None or not self._is_driver_alive():
            self.logger.info("🚗 드라이버가 닫혀 있어 재초기화합니다.")
            self.driver = self._initialize_driver()

    def _default_selenium_retry_decorator(self, func: Callable[..., Any]) -> Callable[..., Any]:

        """
        기본 Selenium WebDriver 재시도 데코레이터

        - 최대 3회 재시도
        - WebDriverException, TimeoutException 발생 시 재시도
        - 재시도 전후에 로그 출력

        Args:
            func (callable): 재시도 적용할 함수

        Returns:
            callable: 재시도 기능이 적용된 함수

        Example:
            >>> @self._default_selenium_retry_decorator
            ... def do_something():
            ...     pass
        """
        return retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(exp_base=4, multiplier=3, min=4, max=60),
            before_sleep=before_sleep_log(self.logger, logging.INFO),
            after=after_log(self.logger, logging.DEBUG),
            retry=retry_if_exception_type((WebDriverException, TimeoutException)),
            reraise=True
        )(func)

    # def perform_request(
    #         self,
    #         url,
    #         scroll_settings: SeleniumClientScrollConfig = SeleniumClientScrollConfig(),
    #         selenium_retry_decorator=None,
    # ):
    #     """
    #     지정한 URL을 Selenium으로 요청하고 필요 시 스크롤을 내려 모든 콘텐츠를 로드한 후
    #     HTML 파싱 결과를 반환합니다.
    #
    #     Args:
    #         url (str): 접속할 웹 페이지 URL
    #         scroll_settings (SeleniumClientScrollConfig, optional): 스크롤 관련 설정 객체.
    #             scroll=True일 경우 스크롤을 아래로 내려서 동적 콘텐츠 로딩 시도.
    #             기본값은 SeleniumClientScrollConfig()의 기본 설정.
    #         selenium_retry_decorator (callable, optional): 재시도용 데코레이터 함수.
    #             기본 재시도 조건을 사용할 경우 None으로 둠.
    #
    #     Example:
    #             # SeleniumClient 인스턴스 생성
    #             client = SeleniumClient()
    #
    #             query = quote("온코크로스")
    #             ds, de = "2025.04.11", "2025.05.07"
    #
    #             base_url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&query={query}&sm=tab_opt&sort=2&photo=0&field=0&pd=3&ds={ds}&de={de}"
    #
    #             # 스크롤 설정
    #             scroll_settings = SeleniumClientScrollConfig(scroll=True, trial=3, delay=3)
    #
    #             try:
    #                 # 요청 실행
    #                 print("🔄 요청 중...")
    #
    #                 l1 = get_logger("[Before] 재시도 테스트", logging.INFO)
    #
    #                 custom_retry = retry(
    #                     stop=stop_after_attempt(5),  # 최대 3회 시도 후 중지
    #                     wait=wait_exponential(exp_base=1, multiplier=1, min=1, max=60),  # 지수적으로 증가하는 대기 시간 설정
    #                     before_sleep=before_sleep_log(l1, logging.INFO),  # 재시도 전에 로그 출력
    #                     after=after_log(l1, logging.DEBUG),  # 재시도 후 디버그 로그 출력
    #                     retry=retry_if_exception_type((WebDriverException, TimeoutException))
    #                 )
    #
    #                 html = client.request_with_retry(
    #                     base_url,
    #                     scroll_settings=scroll_settings,
    #                     selenium_retry_decorator=custom_retry
    #                 )
    #
    #                 print("📄 페이지 로드 완료, HTML 내용 일부:")
    #                 print("요청완료. ,", html.prettify()[:100])
    #
    #                 # print(html).
    #             except Exception as e:
    #                 print(f"❌ 요청 중 오류 발생: {e}")
    #             finally:
    #                 # 크롤러 종료
    #                 client.close()
    #
    #     Returns:
    #         BeautifulSoup: 요청한 페이지의 HTML 파싱 결과 객체
    #
    #     Raises:
    #         WebDriverException, TimeoutException: 재시도 후에도 실패 시 예외 발생
    #     """
    #
    #     retry_decorator = selenium_retry_decorator or self._default_selenium_retry_decorator
    #
    #     @retry_decorator
    #     def _do_retry_with_retry():
    #         try:
    #             self._ensure_driver()  # ✅ 드라이버 상태 확인 및 필요 시 재초기화
    #             self.logger.info(f"🔄 요청 중... {url}")
    #             self.driver.get(url)
    #             time.sleep(5)
    #
    #             if scroll_settings.scroll:
    #                 self.scroll_to_bottom(trial=scroll_settings.trial, delay=scroll_settings.delay)
    #
    #             html = BeautifulSoup(self.driver.page_source, "lxml")
    #             return html
    #         except Exception as e:
    #             self.logger.exception(f"❌ 요청 중 오류 발생: {e}")
    #             raise
    #         finally:
    #             self.close()
    #
    #     return _do_retry_with_retry()

    def perform_request(
        self,
        url: str,
        scroll_settings: SeleniumClientScrollConfig = SeleniumClientScrollConfig(),
        selenium_retry_decorator=None,
    ) -> BeautifulSoup:
        """
        Selenium으로 URL 접속 후, 필요 시 스크롤을 내려 모든 콘텐츠를 로드하고
        페이지 HTML을 BeautifulSoup 객체로 반환합니다.

        Args:
            url (str): 요청할 웹 페이지 URL
            scroll_settings (SeleniumClientScrollConfig, optional): 스크롤 설정 객체
            selenium_retry_decorator (callable, optional): 재시도 데코레이터, 기본값 사용 시 None

        Returns:
            BeautifulSoup: 페이지 소스의 파싱 결과 객체

        Raises:
            WebDriverException, TimeoutException: 재시도 실패 시 예외 발생

        Example:
            >>> client = SeleniumClient()
            >>> html = client.perform_request("https://example.com", scroll_settings=SeleniumClientScrollConfig(scroll=True))
            >>> print(html.title.text)
        """
        retry_decorator = selenium_retry_decorator or self._default_selenium_retry_decorator

        @retry_decorator
        def _request_with_retry():
            self._ensure_driver()
            self._load_url(url)
            if scroll_settings.scroll:
                self.scroll_to_bottom(trial=scroll_settings.trial, delay=scroll_settings.delay)
            return BeautifulSoup(self.driver.page_source, "lxml")

        return _request_with_retry()

    def _load_url(self, url: str):
        """
        WebDriver로 URL 로드 후 잠시 대기

        Args:
            url (str): 접속할 URL

        Example:
            >>> self._load_url("https://example.com")
        """
        self.logger.info(f"🔄 요청 중... {url}")
        self.driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기

    def scroll_to_bottom(self, trial: int = 3, delay: int = 2):
        """
        페이지 하단까지 스크롤을 수행하는 메인 함수.

        지정한 최대 시도 횟수만큼 페이지 하단으로 스크롤하며,
        더 이상 페이지 높이가 변하지 않으면 중단합니다.

        Args:
            trial (int): 최대 스크롤 시도 횟수 (기본값: 3)
            delay (int): 각 스크롤 시도 후 대기 시간(초) (기본값: 2)

        Example:
            >>> driver = SeleniumDriver(...)
            >>> driver.scroll_to_bottom(trial=5, delay=1)
        """
        prev_height = self._get_scroll_height()
        for i in range(trial):
            self.logger.info(f"📜 스크롤 실행 중... {i + 1} / {trial}")

            if not self._scroll_once():
                self.logger.error("❌ 스크롤 실패, body 요소를 찾지 못함.")
                break

            time.sleep(delay)

            new_height = self._get_scroll_height()
            if new_height == prev_height:
                self.logger.info("✅ 더 이상 스크롤할 콘텐츠가 없습니다.")
                break

            prev_height = new_height

        self.logger.info("✔️ 스크롤 완료")

    def _get_scroll_height(self) -> int:
        """
        현재 페이지의 전체 높이를 JavaScript로 조회합니다.

        Returns:
            int: 페이지의 scrollHeight 값

        Example:
            >>> height = driver._get_scroll_height()
        """
        return self.driver.execute_script("return document.body.scrollHeight")

    def _scroll_once(self) -> bool:
        """
        body 요소에 포커스를 맞추고 END 키 입력으로 한 번 스크롤을 수행합니다.

        Returns:
            bool: 성공 시 True, 실패 시 False

        Example:
            >>> success = driver._scroll_once()
        """
        try:
            wait = WebDriverWait(self.driver, 5)
            body = wait.until(ec.presence_of_element_located((By.TAG_NAME, "body")))
            body.send_keys(Keys.END)
            return True
        except Exception:
            self.logger.exception("❌ body 요소를 찾을 수 없습니다.")
            return False

    def close(self):
        """
        Selenium WebDriver 종료 메서드

        - driver 인스턴스가 존재할 경우 안전하게 종료함.
        """
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    from tenacity import retry, stop_after_attempt, retry_if_exception_type
    from tenacity import before_sleep_log, after_log
    import logging


    def __main():
        """SeleniumClient를 실행하는 메인 함수
        """

        # SeleniumClient 인스턴스 생성
        client = SeleniumClient()

        query = quote("온코크로스")
        ds, de = "2025.04.11", "2025.05.07"

        base_url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&query={query}&sm=tab_opt&sort=2&photo=0&field=0&pd=3&ds={ds}&de={de}"

        # 스크롤 설정
        scroll_settings = SeleniumClientScrollConfig(scroll=True, trial=3, delay=3)

        try:
            # 요청 실행
            print("🔄 요청 중...")

            l1 = get_logger("[Before] 재시도 테스트", logging.INFO)

            custom_retry = retry(
                stop=stop_after_attempt(3),  # 최대 3회 시도 후 중지
                wait=wait_exponential(exp_base=1, multiplier=1, min=1, max=60),  # 지수적으로 증가하는 대기 시간 설정
                before_sleep=before_sleep_log(l1, logging.INFO),  # 재시도 전에 로그 출력
                after=after_log(l1, logging.DEBUG),  # 재시도 후 디버그 로그 출력
                retry=retry_if_exception_type((WebDriverException, TimeoutException))
            )

            html = client.request_with_retry(
                base_url,
                scroll_settings=scroll_settings,
                selenium_retry_decorator=custom_retry
            )

            print("📄 페이지 로드 완료, HTML 내용 일부:")
            print("요청완료. ,", html.prettify()[:100])

            # print(html).
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        finally:
            # 크롤러 종료
            client.close()
    __main()