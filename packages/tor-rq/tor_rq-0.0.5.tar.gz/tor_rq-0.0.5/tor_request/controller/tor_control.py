from tor_request.controller.base.base_tor_controller import BaseTorController
from tor_request.controller.utiles.renew_tor_ip import renew_tor_ip


class TorController(BaseTorController):
    """
    실제 Tor 제어 기능(IP 갱신)을 수행하는 구현체입니다.

    - 기본 control 포트에서 IP 갱신을 시도하고,
    - 실패 시 가능한 다른 control 포트를 탐색하여 대체 사용합니다.
    """

    def renew_ip(self):
        """
        현재 설정된 control 포트를 사용하여 Tor IP를 갱신합니다.

        실패 시 다른 가능한 control 포트를 자동으로 찾아 재시도합니다.

        Raises:
            RuntimeError: 모든 control 포트에서 IP 갱신 실패 시 발생

        Example:
            >>> controller = TorController()
            >>> controller.renew_ip()
        """
        try:
            self._renew_ip_internal(self.control_port)
        except Exception as e:
            self.logger.warning(f"❌ Tor IP 갱신 중 오류 발생: {e}")
            self._try_fallback_and_renew()

    def _renew_ip_internal(self, port: int):
        """
        지정된 control 포트를 사용하여 Tor IP를 갱신합니다.

        Args:
            port (int): 사용할 control 포트

        Raises:
            Exception: renew_tor_ip 실패 시 예외 전파
        """
        self.logger.debug(f"🔄 Tor IP 갱신 시도 중... (control port: {port})")
        renew_tor_ip(port=port)
        self.logger.info(f"✅ Tor IP 갱신 성공 (control port: {port})")

    def _try_fallback_and_renew(self):
        """
        기본 control 포트로 갱신 실패 시,
        다른 가능한 control 포트를 탐색하여 갱신 시도합니다.

        Raises:
            RuntimeError: 모든 control 포트에서 IP 갱신 실패 시 발생
        """
        fallback_ports = self.scan_possible_tor_ports()

        for config in fallback_ports:
            if config.get("control_open"):
                fallback_port = config["control"]
                self.logger.info(f"🚨 대체 control 포트 발견: {fallback_port} | config: {config}")
                self.control_port = fallback_port

                try:
                    self._renew_ip_internal(fallback_port)
                    return
                except Exception as e:
                    self.logger.warning(f"⚠️ 대체 포트 갱신 실패 (port: {fallback_port}) | {e}")

        # 모든 시도 실패 시 예외 발생
        raise RuntimeError("❌ 모든 Tor control 포트에서 IP 갱신 실패")


if __name__ == "__main__":

    tor = TorController()
    current_ip = tor.get_current_ip()  # 현재 IP 확인
    print(f"현재 Tor IP: {current_ip}")
    print()
    tor.renew_ip()  # IP 갱신 요청
    current_ip = tor.get_current_ip()  # 현재 IP 확인
    print(f"현재 Tor IP: {current_ip}")

    print(tor.scan_possible_tor_ports())