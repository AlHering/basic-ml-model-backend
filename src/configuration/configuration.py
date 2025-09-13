# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from . import paths as PATHS
from . import urls as URLS


"""
Environment file
"""
ENV = load_dotenv(os.path.join(PATHS.PACKAGE_PATH, ".env"))


"""
Backend
"""
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = int("7861")
BACKEND_ENDPOINT_BASE = "/api/v1"

PROJECT_NAME = "ModelHelper"
PROJECT_VERSION = "v0.1"
PROJECT_DESCRIPTION = "Helper Tool for Model management."


"""
Frontend
"""
DEFAULT_FRONTEND_CACHE = {

}


"""
MISC
"""
LOGGER = None
