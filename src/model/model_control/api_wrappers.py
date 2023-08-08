# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import requests
import json
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

    def check_connection(self, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Abstract method for checking connection.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        pass

    @abc.abstractmethod
    def validate_url_responsiblity(self, url: str, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Abstract method for validating the responsiblity for a URL.
        :param url: Target URL.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True, if wrapper is responsible for URL else False.
        """
        pass

    @abc.abstractmethod
    def scrape_available_targets(self, target_type: str, *args: Optional[List], **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for acquring available targets.
        :param target_type: Type of target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: List of entries of given target type.
        """
        pass

    @abc.abstractmethod
    def get_api_url(self, target_type: str, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for a given object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given object.
        """
        pass

    @abc.abstractmethod
    def collect_metadata(self, target_type: str, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for acquring model data by identifier.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        pass

    @abc.abstractmethod
    def normalize_metadata(self, metadata: dict, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for normalizing metadata.
        :param metadata: Metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        pass

    @abc.abstractmethod
    def download_model(self, model: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param model: Model object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_modelversion(self, modelversion: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param modelversion: Model version object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_asset(self, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading an asset.
        :param target_object: Target object to download assets for.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
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
        self.api_base_url = "https://civitai.com/api/v1/"
        self.model_by_versionhash_url = "https://civitai.com/api/v1/model-versions/by-hash/"
        self.model_by_id_url = "https://civitai.com/api/v1/models/"

    def check_connection(self, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Method for checking connection.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        result = requests.get(self.base_url).status_code == 200
        self._logger.info("Connection was successfuly established.") if result else self._logger.warn(
            "Connection could not be established.")
        return result

    def validate_url_responsiblity(self, url: str, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Method for validating the responsiblity for a URL.
        :param url: Target URL.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True, if wrapper is responsible for URL else False.
        """
        return urlparse(url).netloc in self.base_url

    @abc.abstractmethod
    def scrape_available_targets(self, target_type: str, *args: Optional[List], **kwargs: Optional[dict]) -> List[dict]:
        """
        Abstract method for acquring available targets.
        :param target_type: Type of target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: List of entries of given target type.
        """
        pass

    @abc.abstractmethod
    def get_api_url(self, target_type: str, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for a given object.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given object.
        """
        pass

    @abc.abstractmethod
    def collect_metadata(self, target_type: str, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for acquring model data by identifier.
        :param target_type: Type of target object.
        :param target_object: Target object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        pass

    @abc.abstractmethod
    def normalize_metadata(self, metadata: dict, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Abstract method for normalizing metadata.
        :param metadata: Metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        pass

    @abc.abstractmethod
    def download_model(self, model: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param model: Model object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_modelversion(self, modelversion: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param modelversion: Model version object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_asset(self, target_object: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading an asset.
        :param target_object: Target object to download assets for.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass


class LegacyCivitaiAPIWrapper(AbstractAPIWrapper):
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
        self.api_base_url = "https://civitai.com/api/v1/"
        self.model_by_versionhash_url = "https://civitai.com/api/v1/model-versions/by-hash/"
        self.model_by_id_url = "https://civitai.com/api/v1/models/"

    def check_connection(self, *args: Optional[List], **kwargs: Optional[dict]) -> bool:
        """
        Method for checking connection.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfuly else False.
        """
        result = requests.get(self.base_url).status_code == 200
        self._logger.info("Connection was successfuly established.") if result else self._logger.warn(
            "Connection could not be established.")
        return result

    def get_model_page(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring model page for model.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Model page for given model ID.
        """
        return {"hash": self.model_by_versionhash_url, "id": self.model_by_id_url}[identifier] + str(model_id)

    def get_api_url(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> str:
        """
        Abstract method for acquring API URL for model version.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: API URL for given model version ID.
        """
        return {"hash": self.model_by_versionhash_url, "id": self.model_by_id_url}[identifier] + str(model_id)

    def collect_metadata(self, identifier: str, model_id: Any, *args: Optional[List], **kwargs: Optional[dict]) -> dict:
        """
        Method for acquring model data by identifier.
        :param identifier: Type of identification.
        :model_id: Identification of specified type.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Metadata for given model ID.
        """
        self._logger.info(
            f"Fetching metadata for model with '{model_id}' as '{identifier}'...")
        resp = requests.get(self.get_api_url(identifier, model_id), headers={
                            "Authorization": self.authorization})
        try:
            meta_data = json.loads(resp.content)
            if meta_data is not None and not "error" in meta_data:
                self._logger.info(f"Fetching metadata was successful.")
                return meta_data
            else:
                self._logger.warn(f"Fetching metadata failed.")
        except json.JSONDecodeError:
            self._logger.warn(f"Metadata response could not be deserialized.")
            return {}

    def normalize_metadata(self, metadata: dict, **kwargs: Optional[dict]) -> dict:
        """
        Method for normalizing metadata.
        :param metadata: Metadata.
        :param kwargs: Arbitrary keyword arguments.
        :return: Normalized metadata.
        """
        # TODO: Implement, once common metadata format is planned out.
        pass

    def download_model(self, model: Any, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param model: Model object.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def download_asset(self, asset_type: str, url: str, output_path: str) -> bool:
        """
        Method for downloading assets to disk.
        :param asset_type: Asset type.
        :param url: Asset URL.
        :param output_path: Output path.
        :return: True, if process was successful, else False.
        """
        if asset_type == "image":
            return self.downloading_image(url, output_path)

    @internet_utility.timeout(360.0)
    def download_image(self, url: str, output_path: str) -> bool:
        """
        Method for downloading images to disk.
        :param url: Image URL.
        :param output_path: Output path.
        :return: True, if process was successful, else False.
        """
        sleep(2)
        download = requests.get(url, stream=True, headers={
                                "Authorization": self.authorization})
        with open(output_path, 'wb') as file:
            shutil.copyfileobj(download.raw, file)
        del download
        if image_utility.check_image_health(output_path):
            return True
        else:
            return False
