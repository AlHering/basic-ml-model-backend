# -*- coding: utf-8 -*-
import os
import requests
import json
from time import sleep
from copy import deepcopy
import logging
from urllib.parse import urlparse
from typing import Any, Optional, List, Dict, Tuple
from src.utility import json_utility, requests_utility, time_utility


class CivitaiAPIWrapper(object):
    """
    Class, representing civitai API wrapper.
    """

    def __init__(self,
                 api_key: str | None = None,
                 headers: dict | None = None,
                 wait_time: float = 1.5,
                 raw_data_path: str | None = None,
                 logger_overwrite: Any = None) -> None:
        """
        Initiation method.
        :param api_key: Civitai API key which can be created in the civitai user account settings.
        :param headers: Additional headers.
        :param wait_time: Waiting time in seconds between requests or download tries.
        :param raw_data_path: Folder path to backup/output raw data.
            Defaults to None in which case raw data is not saved.
        :param logger_overwrite: Logger overwrite for logging progress.
            Defaults to None in which case the progress is not logged.
        """
        self.logger = logging.Logger(
            f"[CAW{self}]") if logger_overwrite is None else logger_overwrite
        self.api_key = api_key
        self.headers = headers
        if "Authorization" not in headers and self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key

        self.base_url = "https://civitai.com/"
        self.api_base_url = f"{self.base_url}api/v1"

        # TODO: Implement and add creator, post, ...
        self.endpoints = {
            "model": f"{self.api_base_url}/models?sort=Newest&nsfw=true&limit=100",
            "modelversion": f"{self.api_base_url}/model-versions?sort=Newest&nsfw=true&limit=100",
            "image": f"{self.api_base_url}/images?sort=Newest&nsfw=true&limit=100"
        }
        self.identifier_endpoints = {
            "model": {
                "id": f"{self.api_base_url}/models/{{}}"
            },
            "modelversion": {
                "id": f"{self.api_base_url}/model-versions/{{}}",
                "hash": f"{self.api_base_url}/model-versions/by-hash/{{}}"
            }
        }
        self.model_version_by_hash_endpoint = f"{self.model_version_api_endpoint}/by-hash"
        self.wait = wait_time
        self.raw_data_path = raw_data_path
        self.raw_response_path = None
        self.image_path = None
        self.model_path = None
        if raw_data_path:
            os.makedirs(raw_data_path, exist_ok=True)
            self.raw_response_path = os.path.join(raw_data_path, "responses")
            self.image_path = os.path.join(raw_data_path, "images")
            self.model_path = os.path.join(raw_data_path, "models")

        self.last_fetched_url = None
        self.last_fetched_response = None

    @classmethod
    def get_source_name(cls) -> str:
        """
        Returns source name.
        :return: Source name.
        """
        return "civitai.com"

    def get_asset_types(self) -> List[str]:
        """
        Returns available asset types.
        :return: Asset types.
        """
        return [key for key in self.endpoints]

    def get_asset_identifiers(self) -> Dict[str: List[str]]:
        """
        Returns available asset identifiers.
        :return: Asset identifiers.
        """
        return {
            key: [identifier for identifier in self.identifier_endpoints[key]]
            for key in self.identifier_endpoints
        }

    def check_connection(self, **kwargs: Optional[dict]) -> bool:
        """
        Method for checking connection.
        :param kwargs: Arbitrary keyword arguments.
        :return: True if connection was established successfully else False.
        """
        result = requests.get(self.base_url).status_code == 200
        self.logger.info("Connection was successfully established.") if result else self.logger.warning(
            "Connection could not be established.")
        return result

    def validate_url_responsibility(self, url: str) -> bool:
        """
        Method for validating the responsibility for a URL.
        :param url: Target URL.
        :return: True, if wrapper is responsible for URL else False.
        """
        return urlparse(url).netloc in self.base_url

    def scrape_available_asset_metadata(self, asset_type: str, callback: Any = None, start_url: str | None = None, query_params: dict | None = None) -> List[dict]:
        """
        Collects available metadata entries for a target asset type.
        :param asset_type: Asset type out of supported asset types.
        :param callback: Callback to call with collected model data batches.
            Callback should take a list of entries and arbitrary keyword arguments (**kwargs) and return true, if operation was successful else False.
        :param start_url: A starting URL for cursor pagination.
        :param query_params: Query parameters to append to next URL if missing.
        :return: List of entries of given target type.
        """
        result = []
        if callback is None:
            def callback(x: Any, **kwargs: dict) -> bool:
                result.extend(x) if isinstance(x, list) else result.append(x)
                return True

        self.collect_assets_via_api(
            asset_type=asset_type, callback=callback, start_url=start_url, query_params=query_params)
        return result

    def scrape_single_asset_metadata(self, asset_type: str, identifier: str, value: str) -> dict:
        """
        Abstract method for acquiring available metadata entries for a target asset type.
        :param asset_type: Asset type out of supported asset types.
        :param identifier: Identifier type, available through wrapper.
        :param value: identifier value to identify target asset.
        :return: Asset metadata.
        """
        # TODO: Implement
        pass

    def collect_assets_via_api(self, asset_type: str, callback: Any, start_url: str | None = None, query_params: dict | None = None) -> None:
        """
        Method for collecting assets data via api.
        :param asset_type: Asset type out of supported asset types.
        :param callback: Callback to call with collected model data batches.
        :param start_url: A starting URL for cursor pagination.
        :param query_params: Query parameters to append to next URL if missing.
        """
        if start_url:
            next_url = start_url
        else:
            next_url = self.endpoints[asset_type]
        while next_url:
            sleep(self.wait)
            data = self.safely_fetch_api_data(
                next_url, params=query_params, current_try=1)
            current_url = next_url
            next_url = False
            if isinstance(data, dict):
                metadata = data["metadata"]
                self.logger.info(f"Fetched metadata: {metadata}.")
                next_url = metadata.get("nextPage")

                if not callback(data["items"], current_url=current_url, next_url=next_url):
                    self.logger.warning(
                        f"Callback operation failed, aborting instead of fetching '{next_url}'...")
                    next_url = False
            else:
                self.logger.warning(f"Fetched data is no dictionary: {data}")

    def safely_fetch_api_data(self, url: str, params: dict | None = None, current_try: int = 3, max_tries: int = 3) -> dict:
        """
        Method for fetching API data.
        :param url: Target URL.
        :param params: Request query params.
            Defaults to None.
        :param current_try: Current try.
            Defaults to 3, which results in a single fetching try with max_tries at 3.
        :param max_tries: Maximum number of tries.
            Defaults to 3.
        :return: Fetched data or empty dictionary.
        """
        self.logger.info(
            f"Fetching data for '{url}'...")
        self.last_fetched_url = url
        resp = requests.get(url, params=params, headers=self.headers)
        self.last_fetched_response = resp

        try:
            data = json.loads(resp.content)
            if data is not None and not "error" in data:
                self.logger.info(f"Fetching content was successful.")
                if self.raw_response_path:
                    json_utility.save(data, os.path.join(
                        self.raw_response_path, time_utility.get_timestamp() + ".json"))
                return data
            else:
                self.logger.warning(f"Fetching metadata failed.")
        except json.JSONDecodeError:
            self.logger.warning(f"Response content could not be deserialized.")
            if current_try < max_tries:
                sleep(self.wait*2)
                return self.safely_fetch_api_data(url, current_try+1, max_tries=max_tries)
            else:
                return {}

    def compute_asset_url(self,
                          asset_type: str,
                          asset_data: dict) -> str | None:
        """
        Computes an asset URL.
        :param asset_type: Asset type.
        :param asset_data: Asset data.
        :return: Identifying URL of the asset or None in case of failure.
        """
        url = None
        if asset_type == "model":
            url = self.identifier_endpoints["model"]["id"].format(
                asset_data["id"])
        elif asset_type == "modelversion":
            url = self.identifier_endpoints["modelversion"]["id"].format(
                asset_data["id"])
        elif asset_type == "image":
            image_url_parts = [part for part in asset_data["url"].split(
                "/") if not part.lower().startswith("width=")]
            url = "/".join(image_url_parts)
            url.replace("https://imagecache.civitai.com/",
                        "https://image.civitai.com/")
        return url

    def compute_update(self,
                       asset_type: str,
                       reference_data: dict,
                       update_data: dict) -> dict:
        """
        Computes an update for a given asset.
        :param asset_type: Asset type.
        :param reference_data: Reference data.
        :param update_data: Update entry data.
        :return: Updated data.
        """
        if asset_type == "model":
            new_mvs = []
            for new_mv_data in update_data["modelVersions"]:
                if not any(new_mv_data["id"] == mv_data["id"] for mv_data in reference_data["modelVersions"]):
                    new_mvs.append(deepcopy(new_mv_data))
            if new_mvs:
                reference_data["modelVersions"].extend(new_mvs)
        elif asset_type == "modelversion":
            new_images = []
            for new_image in update_data["images"]:
                if not any(new_mv_data["hash"] == mv_data["hash"] for mv_data in reference_data["images"]):
                    new_images.append(deepcopy(new_image))
            if new_images:
                reference_data["images"].extend(new_images)
        elif asset_type == "image":
            if "meta" in update_data and len(str(reference_data.get("meta", ""))) < len(str(update_data["meta"])):
                reference_data["meta"] = update_data["meta"]
            for key in [key for key in update_data if key not in reference_data]:
                reference_data[key] = update_data[key]
        reference_data

    def download_asset(self, asset_url: str, output_path: str) -> None:
        """
        Abstract method for downloading an asset.
        :param asset_url: Asset URL.
        :param output_path: Output path.
        """
        # TODO: Test and refine for different asset types.
        requests_utility.download_web_asset(
            asset_url, output_path=output_path, headers=self.headers)
