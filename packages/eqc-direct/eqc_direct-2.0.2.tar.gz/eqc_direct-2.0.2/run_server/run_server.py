import time
import os
import sys
import logging

# sys.argv[0] is the python script
ip_address = sys.argv[1]
port = sys.argv[2]
log_path = sys.argv[3]

if not os.path.exists(log_path):
    os.makedirs(log_path)
log_file = log_path + "/server_" + time.strftime("%Y%m%d-%H%M%S") + ".log"
logging.basicConfig(
    filename=log_file,
    force=True,
    format=(
        "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
        "-35s %(lineno) -5d: %(message)s"
    ),
    filemode="a",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
rootLogger.addHandler(consoleHandler)

rootLogger.info("Logging to file: %s", log_file)

# https://betterstack.com/community/questions/how-to-log-uncaught-exceptions-in-python/
# Creating a handler
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Will call default excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        # Create a critical level log message with info from the except hook.
    logging.critical(
        "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


# Assign the excepthook to the handler
sys.excepthook = handle_unhandled_exception
if __name__ == "__main__":
    from eqc_direct.server_sim import GrpcServer

    # runs on ThreadPoolExecutor
    server_cls = GrpcServer(
        ip_address=ip_address,
        port=port,
        #       private_key="private.pem",
        #       cert_file="certificate.pem",
    )
    server_cls.serve()
    server_cls.join()
