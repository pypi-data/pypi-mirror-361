"""
Package initialization.

Copyright 2024, Quantum Computing Incorporated
"""

import importlib.metadata
import os

PACKAGE_NAME = __name__
PACKAGE_VERSION = importlib.metadata.version(PACKAGE_NAME)

DEVICE_IP_ADDRESS_DEFAULT = os.getenv("DEVICE_IP_ADDRESS", "localhost")
DEVICE_PORT_DEFAULT = os.getenv("DEVICE_PORT", "50051")
