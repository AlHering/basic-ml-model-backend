# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import logging
from dotenv import dotenv_values
from . import paths as PATHS
from . import urls as URLS


"""
Environment file
"""
ENV = dotenv_values(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Logger
"""


class LOGGER_REPLACEMENT(object):
    """
    Temporary logger replacement class.
    """

    def debug(self, text: str) -> None:
        """
        Method replacement for logging.
        :param text: Text to log.
        """
        print(f"[DEBUG] {text}")

    def info(self, text: str) -> None:
        """
        Method replacement for logging.
        :param text: Text to log.
        """
        print(f"[INFO] {text}")

    def warning(self, text: str) -> None:
        """
        Method replacement for logging.
        :param text: Text to log.
        """
        print(f"[WARNING] {text}")


LOGGER = LOGGER_REPLACEMENT()
# LOGGER = logging.Logger("LMBACKEND")
# LOGGER.setLevel(level=logging.INFO)


"""
Backends
"""
BACKEND_HOST = ENV.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = ENV.get("BACKEND_PORT", "7861")
