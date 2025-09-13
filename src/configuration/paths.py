# -*- coding: utf-8 -*-
import os


"""
Base paths
"""
PACKAGE_PATH = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SOURCE_PATH = os.path.join(PACKAGE_PATH, "src")
DATA_PATH = os.path.join(PACKAGE_PATH, "data")


"""
Frontend paths
"""
FRONTEND_CACHE = os.path.join(DATA_PATH, "frontend_cache.json")