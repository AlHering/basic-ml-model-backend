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
from . import flask_frontend_config
from . import streamlit_frontend_config


"""
Environment file
"""
ENV = dotenv_values(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Logger
"""
LOGGER = logging.Logger("LMBACKEND")


"""
Backends
"""
BACKEND_HOST = ENV.get("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = ENV.get("BACKEND_PORT", "7861")

