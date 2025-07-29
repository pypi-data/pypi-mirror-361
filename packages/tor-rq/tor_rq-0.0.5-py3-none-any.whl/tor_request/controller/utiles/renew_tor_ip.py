import logging
import time

from stem import Signal
from stem.control import Controller
from tor_request.utiles.get_logger import get_logger

def renew_tor_ip(port=9051):
    """
    Tor 네트워크에 새로운 회선을 요청하여 IP를 갱신하는 함수입니다.

    기본적으로 로컬의 Tor ControlPort (기본 포트: 9051)에 연결한 뒤,
    인증을 수행하고, NEWNYM 시그널을 전송하여 새로운 IP로 회선을 재설정합니다.

    예외 발생 시 오류 메시지를 출력합니다.

    Args:
        port (int): Tor ControlPort의 포트 번호 (기본값: 9051)
    """
    logger = get_logger(name=__name__, level=logging.INFO)
    try:
        # Tor 컨트롤 포트에 연결 (기본적으로 9051 포트 사용)
        with Controller.from_port(port=port) as controller:
            # 인증 수행 (기본적으로 cookie 인증 사용)
            # 비밀번호 인증이 설정된 경우 → controller.authenticate(password='your_password') 사용
            controller.authenticate()

            # Tor에게 NEWNYM 시그널 전송 → 새로운 IP 회선 요청
            controller.signal(Signal.NEWNYM)

            logger.info("✅ Tor IP가 갱신되었습니다.")
            time.sleep(2)
    except Exception as e:
        # 예외 발생 시 오류 메시지 출력
        logger.exception(f"❌ Tor IP 갱신 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    # 스크립트가 직접 실행될 때 Tor IP 갱신 요청
    renew_tor_ip()
    print("Tor IP 갱신 요청이 완료되었습니다.")