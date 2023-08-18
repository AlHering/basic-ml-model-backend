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
from src.utility.bronze import requests_utility
from src.model.model_control.model_database import ModelDatabase, DEFAULT_DB_PATH
from src.model.model_control.model_handler import DiffusionModelHandler

from src.model.model_control.api_wrapper import CivitaiAPIWrapper


if __name__ == "__main__":
    output_path = "/mnt/Workspaces/Workspaces/projects/basic-language-model-backend/data/testing/diffusion_models/disneyPixarCartoon_v10.safetensors"
    """wrapper = CivitaiAPIWrapper()
    wrapper.download_model(
        model="",
        path=output_path
    )"""

    requests_utility.download_web_asset(
        "https://civitai.com/api/download/models/69832", output_path=output_path)
