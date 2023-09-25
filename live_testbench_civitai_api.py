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
from src.utility.bronze import json_utility
from src.utility.gold.filter_mask import FilterMask
from src.configuration import configuration as cfg
from src.model.model_control.model_database import ModelDatabase, DEFAULT_DB_PATH

from src.model.model_control.api_wrapper import CivitaiAPIWrapper


if __name__ == "__main__":
    # if os.path.exists(DEFAULT_DB_PATH):
    #    os.remove(DEFAULT_DB_PATH)
    db = ModelDatabase(database_uri=None, schema="civitai", verbose=True)
    wrapper = CivitaiAPIWrapper()
    # handler.scrape_available_models(wrapper.get_source_name())
