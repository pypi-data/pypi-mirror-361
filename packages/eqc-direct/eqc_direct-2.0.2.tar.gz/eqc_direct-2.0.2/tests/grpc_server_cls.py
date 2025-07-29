from eqc_direct.server_sim import GrpcServer
import threading
import time


class ServerForTest:
    """
    Used for unittests only
    Starts a server on a thread and then sets stop event and joins when done
    """

    def __init__(
        self, ip_address, port, private_key: str = None, cert_file: str = None
    ):
        self.server_cls = GrpcServer(
            ip_address=ip_address,
            port=port,
            private_key=private_key,
            cert_file=cert_file,
        )
        self.server_thread = threading.Thread(target=self.server_cls.serve)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()
        time.sleep(2)

    def stop(self):
        self.server_cls.stop()
        self.server_thread.join()
