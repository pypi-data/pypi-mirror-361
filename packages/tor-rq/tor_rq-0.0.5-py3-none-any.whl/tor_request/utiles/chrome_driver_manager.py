import os
import ssl
import sys
import certifi
import urllib.request
import subprocess
from pathlib import Path
from typing import Optional
from tor_request.utiles.get_logger import get_logger, logging
from webdriver_manager.chrome import ChromeDriverManager as WDMChromeDriverManager
import platform
import stat

class ChromeDriverManager:
    """
    webdriver_manager 기반의 ChromeDriver 경로를 관리하는 클래스.

    주요 기능:
    - WDM 캐시 디렉토리에서 chromedriver 탐색
    - chromedriver 실행 테스트
    - 기본 설치 및 SSL 인증서 문제 시 우회 설치 지원
    """

    cached_path: Optional[str] = None
    _logger = None

    @classmethod
    def get_logger(cls):
        """클래스 단위 logger 객체 초기화 및 반환"""
        if cls._logger is None:
            cls._logger = get_logger(__name__, logging.INFO)
        return cls._logger

    @classmethod
    def _get_chromedriver_cache_dir(cls) -> str:
        """
        webdriver_manager의 기본 chromedriver 캐시 경로 반환
        예: ~/.wdm/drivers/chromedriver
        """
        return os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver")

    @classmethod
    def _is_chromedriver_file(cls, filename: str) -> bool:
        """
        chromedriver 실행 파일 여부 확인
        - macOS/Linux: 'chromedriver'
        - Windows: 'chromedriver.exe'
        """
        return filename in {"chromedriver", "chromedriver.exe"}

    @classmethod
    def _search_chromedriver_in_cache(cls, base_path: str) -> Optional[str]:
        """
        주어진 경로 하위에서 chromedriver 파일을 탐색하여 최초 발견 경로를 반환
        """
        logger = cls.get_logger()
        try:
            for root, _, files in os.walk(base_path):
                for file in files:
                    if cls._is_chromedriver_file(file):
                        candidate = os.path.join(root, file)
                        logger.info(f"캐시된 chromedriver 발견: {candidate}")
                        return candidate
        except Exception as e:
            logger.warning(f"캐시 탐색 중 오류 발생: {e}")

        logger.info("캐시된 chromedriver를 찾을 수 없습니다.")
        return None

    @classmethod
    def _get_chromedriver_platforms(cls) -> list[str]:
        """
        현재 플랫폼에 맞는 webdriver_manager 디렉토리 후보 리스트 반환
        우선순위 순서대로: ['mac64', 'mac_arm64'], ['win64', 'win32'], ['linux64']
        """
        system = sys.platform
        machine = platform.machine()

        if system == "darwin":
            return ["mac64", "mac_arm64"] if machine == "arm64" else ["mac64", "mac_arm64"]
        elif system.startswith("linux"):
            return ["linux64"]
        elif system.startswith("win"):
            return ["win64"] if machine in ("AMD64", "x86_64") else ["win64"]
        else:
            raise RuntimeError(f"지원되지 않는 플랫폼: {system} ({machine})")

    @classmethod
    def _find_cached_chromedriver(cls) -> Optional[str]:
        """
        webdriver_manager 캐시 디렉토리에서 가장 최신 버전의 chromedriver 경로를 반환
        """
        logger = cls.get_logger()
        base_path = cls._get_chromedriver_cache_dir()
        platform_dirs = cls._get_chromedriver_platforms()

        for platform_dir in platform_dirs:
            platform_path = os.path.join(base_path, platform_dir)

            if not os.path.exists(platform_path):
                logger.info(f"플랫폼 캐시 디렉토리 없음: {platform_path}")
                continue

            try:
                versions = sorted(
                    os.listdir(platform_path),
                    reverse=True,
                    key=lambda v: tuple(int(part) for part in v.split(".") if part.isdigit())
                )
                for version in versions:
                    version_path = os.path.join(platform_path, version)
                    driver = cls._search_chromedriver_in_cache(version_path)
                    if driver:
                        logger.info(f"최신 캐시된 chromedriver 사용: {driver}")
                        return driver
            except Exception as e:
                logger.warning(f"[{platform_dir}] 버전 탐색 중 오류 발생: {e}")

        logger.info("사용 가능한 chromedriver 캐시를 찾지 못했습니다.")
        return None

    @classmethod
    def _test_chromedriver(cls, exe_path: str):
        """
        주어진 chromedriver 실행 파일이 정상 동작하는지 subprocess로 테스트
        """
        logger = cls.get_logger()
        logger.info(f"chromedriver 실행 테스트 중: {exe_path}")

        # 실행 권한이 없는 경우 자동으로 권한 추가
        if not os.access(exe_path, os.X_OK):
            logger.warning(f"chromedriver 실행 권한 없음. 권한 부여 시도: {exe_path}")
            try:
                st = os.stat(exe_path)
                os.chmod(exe_path, st.st_mode | stat.S_IEXEC)
            except Exception as chmod_err:
                logger.exception(f"권한 부여 실패: {chmod_err}")
                raise

        subprocess.run([exe_path, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("chromedriver 실행 테스트 성공")

    @classmethod
    def _try_cached_path(cls) -> Optional[str]:
        """
        클래스 변수에 저장된 cached_path가 존재하고 유효한지 확인하고 반환
        """
        logger = cls.get_logger()
        if cls.cached_path and Path(cls.cached_path).exists():
            logger.info(f"캐시된 chromedriver 경로 존재: {cls.cached_path}, 테스트 실행")
            try:
                cls._test_chromedriver(cls.cached_path)
                return cls.cached_path
            except Exception as e:
                logger.warning(f"캐시된 경로 테스트 실패: {e}")
        return None

    @classmethod
    def _set_urllib_ssl_context(cls):
        """
        macOS용: urllib에서 SSL 검증 우회를 위한 context 설정
        """
        logger = cls.get_logger()
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        try:
            urllib.request.urlopen(url="https://google.com", context=ssl_context)
            logger.info("SSL 인증서 확인 성공")
        except Exception:
            logger.warning("SSL 인증서 확인 실패, 우회 모드 적용")
        ssl._create_default_https_context = lambda: ssl_context

    @classmethod
    def _set_env_ssl_verify_false(cls):
        """
        macOS 외 환경용: webdriver_manager 환경변수로 SSL 검증 비활성화
        """
        os.environ["WDM_SSL_VERIFY"] = "0"

    @classmethod
    def _force_install_without_ssl(cls):
        """
        SSL 인증서 우회 설정을 적용하여 urllib 또는 webdriver_manager가 SSL 검증을 무시하도록 구성

        - macOS: urllib 기본 SSL context 우회
        - 기타: 환경변수 'WDM_SSL_VERIFY=0' 설정
        """
        logger = cls.get_logger()

        if sys.platform == "Darwin":
            cls._set_urllib_ssl_context()
        else:
            cls._set_env_ssl_verify_false()

        logger.info("SSL 우회 설치 구성이 완료되었습니다.")

    @classmethod
    def _try_wdm_cache(cls) -> Optional[str]:
        """
        WDM의 로컬 캐시 디렉토리에서 chromedriver 경로를 탐색하여 반환
        """
        logger = cls.get_logger()
        path = cls._find_cached_chromedriver()
        if path:
            try:
                cls._test_chromedriver(path)
                cls.cached_path = path
                return path
            except Exception as e:
                logger.warning(f"WDM 캐시된 chromedriver 테스트 실패: {e}")
        return None

    @classmethod
    def _try_install(cls, use_ssl_bypass: bool = False) -> Optional[str]:
        """
        webdriver_manager를 사용하여 chromedriver 설치 시도
        - use_ssl_bypass가 True인 경우, SSL 인증서 검증을 우회한 상태로 시도
        """
        logger = cls.get_logger()

        if use_ssl_bypass:
            logger.info("SSL 우회 설치 시도")
            cls._force_install_without_ssl()
        else:
            logger.info("기본 설치 시도")

        try:
            path = WDMChromeDriverManager().install()
            cls._test_chromedriver(path)
            cls.cached_path = path
            logger.info(f"chromedriver 설치 성공: {path}")
            return path
        except Exception as e:
            if use_ssl_bypass:
                logger.exception(f"SSL 우회 설치 실패: {e}")
            else:
                logger.warning(f"기본 설치 실패: {e}")
        return None

    @classmethod
    def drvier_install_with_path(cls) -> str:
        """
        ChromeDriver 경로를 단계별로 확보하여 반환
        순서:
            1) 클래스 캐시 경로 테스트
            2) WDM 캐시 디렉토리 탐색
            3) 기본 설치 시도
            4) SSL 우회 설치 시도
        실패 시 빈 문자열 반환
        """
        logger = cls.get_logger()

        for step in [
            cls._try_cached_path,
            cls._try_wdm_cache,
            lambda: cls._try_install(use_ssl_bypass=False),
            lambda: cls._try_install(use_ssl_bypass=True),
        ]:
            result = step()
            if result:
                return result

        logger.error("모든 시도 실패: chromedriver 경로 획득 실패")
        return ""

if __name__ == "__main__":
    print(platform.machine())
    path = ChromeDriverManager.drvier_install_with_path()
    print(f"ChromeDriver Path: {path}")
