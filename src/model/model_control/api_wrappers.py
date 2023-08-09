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
import copy
from time import sleep
from urllib.parse import urlparse
import shutil
from typing import Any, Optional, List
from src.utility.silver import image_utility, internet_utility
from src.configuration import configuration as cfg
import abc


class AbstractAPIWrapper(abc.ABC):
    """
    Abstract class, representing a API wrapper object.
    Such wrappers are used for connecting to model services.
    """
    @abc.abstractclassmethod
    def get_source_name(cls) -> str:
        """
        Abstract classmethod for retrieving source name.
        :return: Source name.
        """
        pass

    def check_connection(self, **kwargs: Optional[dict]) -> bool:
        """
        Abstract method for checking connection.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        pass

    @abc.abstractmethod
    def validate_url_responsiblity(self, url: str, **kwargs: Optional[dict]) -> bool:
        """
        Abstract method for validating the responsiblity for a URL.
        :param url: Target URL.
        :param kwargs: Arbitrary keyword arguments.
        :return: True, if wrapper is responsible for URL else False.
        """
        pass

    @abc.abstractmethod
    def scrape_available_targets(self, target_type: str, **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for acquring available targets.
        :param target_type: Type of target object.
        :param kwargs: Arbitrary keyword arguments.
        :return: List of entries of given target type.
        """
        pass

    @abc.abstractmethod
    def get_api_url(self, target_type: str, target_object: Any, **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for a given object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given object.
        """
        pass

    @abc.abstractmethod
    def collect_metadata(self, target_type: str, target_object: Any, **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for acquring model data by target type and object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        pass

    @abc.abstractmethod
    def normalize_metadata(self, target_type: str, metadata: dict, **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for normalizing metadata.
        :param target_type: Type of target object.
        :param metadata: Metadata.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        pass

    @abc.abstractmethod
    def download_model(self, model: Any, path: str, **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param model: Model object.
        :param path: Path to download assets to.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_modelversion(self, modelversion: Any, path: str, **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param modelversion: Model version object.
        :param path: Path to download assets to.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_assets(self, target_type: str, target_object: Any, asset_type: str, path: str, **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for downloading assets for a target object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param asset_type: Asset type.
        :param path: Path to download assets to.
        :param kwargs: Arbitrary keyword arguments.
        :return: Asset data dictionaries.
        """
        pass


class CivitaiAPIWrapper(AbstractAPIWrapper):
    """
    Class, representing civitai API wrapper.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        self._logger = cfg.LOGGER
        self.authorization = cfg.ENV["CIVITAI_API_KEY"]
        self.base_url = "https://civitai.com/"
        self.api_base_url = f"{self.base_url}api/v1"
        self.modelversion_by_hash_endpoint = f"{self.api_base_url}/model-versions/by-hash/"
        self.model_api_endpoint = f"{self.api_base_url}/models/"
        self.wait = 1.5

    def get_source_name(self) -> str:
        """
        Classmethod for retrieving source name.
        :return: Source name.
        """
        return "civitai"

    def check_connection(self, **kwargs: Optional[dict]) -> bool:
        """
        Method for checking connection.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        result = requests.get(self.base_url).status_code == 200
        self._logger.info("Connection was successfuly established.") if result else self._logger.warn(
            "Connection could not be established.")
        return result

    def validate_url_responsiblity(self, url: str, **kwargs: Optional[dict]) -> bool:
        """
        Method for validating the responsiblity for a URL.
        :param url: Target URL.
        :param kwargs: Arbitrary keyword arguments.
        :return: True, if wrapper is responsible for URL else False.
        """
        return urlparse(url).netloc in self.base_url

    def scrape_available_targets(self, target_type: str, **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for acquring available targets.
        :param target_type: Type of target object.
        :param kwargs: Arbitrary keyword arguments.
            'callback': A callback for adding batches of scraping results while scraping process runs.
                If a callback for adding results is given, this method will return an empty list.
            'model': A target model for constraining target model versions to be scraped.
        :return: List of entries of given target type.
        """
        result = []
        callback = kwargs.get("callback")
        if callback is None:
            def callback(x: Any) -> None: result.extend(
                x) if isinstance(x, list) else result.append(x)
        if target_type == "model":
            self.collect_models_via_api(callback)
        elif target_type == "modelversion":
            target_model = kwargs.get("model")
            if target_model is not None:
                metadata = self.safely_fetch_api_data(
                    target_model.url) if target_model.metadata is None else target_model.metadata
                if metadata is not None:
                    callback(metadata["modelVersions"])
            else:
                def modelversion_callback_gateway(x: Any) -> None:
                    if not isinstance(x, list):
                        x = [x]
                    for entry in x:
                        callback(entry["modelVersions"])
                self.collect_models_via_api(modelversion_callback_gateway)
        return result

    def collect_models_via_api(self, callback: Any) -> None:
        """
        Method for collecting model data via api.
        :param callback: Callback to call with collected model data batches.
        """
        next_url = self.model_api_endpoint
        while next_url:
            sleep(self.wait)
            data = self.safely_fetch_api_data(next_url)
            next_url = False
            if data:
                metadata = data["metadata"]
                next_url = metadata.get("nextPage")
                if next_url:
                    next_url += "&limit=100"
                callback(data["items"])

    def get_api_url(self, target_type: str, target_object: Any, **kwargs: Optional[dict]) -> Optional[str]:
        """
        Abstract method for acquring API URL for a given object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given object.
        """
        if target_type == "modelversion":
            return self.model_by_versionhash_url + str(target_object.sha256)

    def collect_metadata(self, target_type: str, target_object: Any, **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for acquring model data by identifier.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        return self.safely_fetch_api_data(target_object.url)

    def safely_fetch_api_data(self, url: str) -> dict:
        """
        Method for fetching API data.
        :param url: Target URL.
        :return: Fetched data or empty dictionary.
        """
        self._logger.info(
            f"Fetching data for '{url}'...")
        resp = requests.get(url, headers={
                            "Authorization": self.authorization})
        try:
            data = json.loads(resp.content)
            if data is not None and not "error" in data:
                self._logger.info(f"Fetching metadata was successful.")
                return data
            else:
                self._logger.warn(f"Fetching metadata failed.")
        except json.JSONDecodeError:
            self._logger.warn(f"Metadata response could not be deserialized.")
            return {}

    def normalize_metadata(self, target_type: str, metadata: dict, **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for normalizing metadata.
        :param target_type: Type of target object.
        :param metadata: Metadata.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        normalized = {}
        if target_type == "model":
            normalized = {
                "name": metadata["name"],
                "type": metadata["type"].upper(),
                "task": {
                    "checkpoint": "image_generation",
                    "textualinversion": "image_generation_guidance",
                    "hypernetwork": "image_generation_guidance",
                    "aestheticgradient": "image_generation_guidance",
                    "lora": "image_generation_guidance",
                    "embedding": "image_generation_guidance",
                    "lycoris": "image_generation_guidance",
                    "vae": "image_generation_guidance",
                    "controlnet": "image_generation_guidance",
                    "poses": "image_generation_guidance",
                    "wildcards": "image_generation_guidance",
                    "upscaler": "image_upscaling",
                    "other": None,
                }[metadata["type"].lower()],
                "architecture": "stablediffusion",
                "meta_data": copy.deepcopy(metadata),
                "url": f"https://civitai.com/api/v1/models/{metadata['id']}",
                "source": self.get_source_name()
            }
        elif target_type == "modelversion":
            normalized = {
                "name": metadata["name"],
                "basemodel": metadata["baseModel"],
                "meta_data": copy.deepcopy(metadata),
                "url": f"https://civitai.com/api/v1/model-versions/{metadata['id']}",
                "source": self.get_source_name()
            }
        return normalized if normalized else metadata

    def download_model(self, model: Any, path: str, **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param model: Model object.
        :param path: Absolute path to download model to.
        :param kwargs: Arbitrary keyword arguments.
        """
        if model.path is not None:
            if not os.path.exists(model.path):
                os.makedirs()

    def download_modelversion(self, modelversion: Any, path: str, **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param modelversion: Model version object.
        :param path: Absolute path to download model version to.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def download_assets(self, target_type: str, target_object: Any, asset_type: str, path: str, **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for downloading assets for a target object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param asset_type: Asset type.
        :param path: Path to download assets to.
        :param kwargs: Arbitrary keyword arguments.
        :return: Asset data dictionaries.
        """
        pass
