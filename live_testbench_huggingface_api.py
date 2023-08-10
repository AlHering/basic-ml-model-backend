# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
import requests
import json
from time import sleep
from src.utility.bronze import json_utility
from src.utility.gold.filter_mask import FilterMask
from src.configuration import configuration as cfg
from src.model.model_control.model_database import ModelDatabase, DEFAULT_DB_PATH
from src.model.model_control.model_handlers import LanguageModelHandler

from src.model.model_control.api_wrappers import HuggingfaceAPIWrapper


if __name__ == "__main__":
    # if os.path.exists(DEFAULT_DB_PATH):
    #    os.remove(DEFAULT_DB_PATH)
    db = ModelDatabase(database_uri=None, schema="huggingface", verbose=True)
    wrapper = HuggingfaceAPIWrapper()
    handler = LanguageModelHandler(
        database=db,
        model_folder=cfg.PATHS.TEST_PATH + "/text_generation_models",
        cache_path=cfg.PATHS.TEST_PATH + "/text_generation_models_cache.json",
        apis={
            wrapper.get_source_name(): wrapper,
        }
    )
    handler.scrape_available_models(wrapper.get_source_name())
