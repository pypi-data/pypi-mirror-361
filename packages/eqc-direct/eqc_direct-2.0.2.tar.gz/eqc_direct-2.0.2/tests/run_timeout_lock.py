import time

from eqc_direct.client import EqcClient


if __name__ == "__main__":
    eqc_client = EqcClient()
    lock_id, _, _ = eqc_client.wait_for_lock()
    start_second_wait = time.time()
    print(eqc_client.wait_for_lock())
    print("Time wait:", time.time() - start_second_wait)
