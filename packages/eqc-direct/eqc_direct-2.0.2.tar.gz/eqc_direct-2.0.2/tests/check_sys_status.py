import sys
import time
from multiprocessing import Pool
from eqc_direct.eqc_client import EqcClient
import numpy as np


def check_status():
    eqc_client = EqcClient()
    resp = eqc_client.system_status()
    print(resp)
    print("Float 32 type", ham_mat_32.dtype)


if __name__ == "__main__":
    check_status()
