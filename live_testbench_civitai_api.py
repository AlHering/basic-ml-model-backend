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
from src.configuration import configuration as cfg
from src.model.model_control.model_database import ModelDatabase, DEFAULT_DB_PATH
from src.model.model_control.api_wrappers import CivitaiAPIWrapper


RELIBERATE_MODEL_ID = 79754

if __name__ == "__main__":
    model_api_url_by_id = f"https://civitai.com/api/v1/models/{RELIBERATE_MODEL_ID}"

    db = ModelDatabase(database_uri=None, schema="civitai", verbose=True)
    model_id = db.post_object("model",
                              **{
                                  "path": "myPath",
                                  "architecture": "sd1.5",
                                  "url": model_api_url_by_id
                              })
    wrapper = CivitaiAPIWrapper()

    print(f"Check connection: {wrapper.check_connection()}")
    print(
        f"Check validation: {wrapper.validate_url_responsiblity(model_api_url_by_id)}")
    print(
        f"Fetch metadata ...")
    model = db.get_object_by_id("model", model_id)
    print(model)
    json_utility.save(wrapper.safely_fetch_api_data(
        model_api_url_by_id), DEFAULT_DB_PATH + ".json")
