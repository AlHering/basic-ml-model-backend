# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os

"""
Base 
"""
PACKAGE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(
    os.path.dirname(__file__))))
SOURCE_PATH = os.path.join(PACKAGE_PATH, "src")
DOCS_PATH = os.path.join(PACKAGE_PATH, "docs")
SUBMODULE_PATH = os.path.join(SOURCE_PATH, "submodules")
DATA_PATH = os.path.join(PACKAGE_PATH, "data")
PLUGIN_PATH = os.path.join(SOURCE_PATH, "plugins")
DUMP_PATH = os.path.join(DATA_PATH, "processes", "dumps")


"""
Machine Learning Models
"""
TEXTGENERATION_MODEL_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "MODELS")
TEXTGENERATION_LORA_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "LORAS")
EMBEDDING_MODEL_PATH = os.path.join(
    PACKAGE_PATH, "machine_learning_models", "EMBEDDING_MODELS")
E5_LARGE_V3_PATH = os.path.join(
    EMBEDDING_MODEL_PATH, "intfloat_e5-large-v2")
INSTRUCT_XL_PATH = os.path.join(
    EMBEDDING_MODEL_PATH, "hkunlp_instructor-xl")

"""
Backends
"""
BACKEND_PATH = os.path.join(DATA_PATH, "backend")
