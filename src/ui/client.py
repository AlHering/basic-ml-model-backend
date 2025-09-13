# -*- coding: utf-8 -*-
import asyncio
import os
import requests
from pydantic import BaseModel
from enum import Enum
import json
import re
from uuid import UUID
from copy import deepcopy
from typing import List, Dict, Generator
from src.backend.backend_server import DatabaseInteraction, DatabaseRequest, BaseRequest, BaseResponse, Endpoints
from src.backend.model_importers.model_importers import ModelImporter
from src.configuration import configuration as cfg


class Client:
    """
    Client class.
    """

    def __init__(self, base_api_url: str = f"http://{cfg.BACKEND_HOST}:{cfg.BACKEND_PORT}{cfg.BACKEND_ENDPOINT_BASE}"):
        """
        Initiation method.
        :param base_api_url: Backend server base API URL.
        """
        self.base_api_url = base_api_url
        self.cache = {"collection": {}, "model": {},
                      "importer": self.get_available_importers()}
        self.interact_with_database(method="get_all", object_type="collection")
        self.interact_with_database(method="get_all", object_type="model")

    def get_available_importers(self) -> dict:
        """
        Returns available model importers.
        :return: Model importer dictionary.
        """
        return {
            "default": ModelImporter
        }

    def _send_request(self, request: DatabaseRequest | BaseRequest) -> dict | None:
        """
        Send a request to the backend server.
        :param request: Request.
        :return: Response or None if decoding failed.
        """
        response = requests.post(
            f"{self.base_api_url}/database-interaction",
            json=request.model_dump()
        )
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return None

    def _send_stream_request(self, request: DatabaseRequest | BaseRequest, timeout: float | None = None) -> Generator[dict, None, None]:
        """
        Send a request for streamed response to the backend server.
        :param service: Service name.
        :param input_package: Input service package.
        :param timeout: Timeout.
        :return: Response generator.
        """
        with requests.post(self.api_base + Endpoints.service_stream, json=request.model_dump(), stream=True) as response:
            accumulated = ""
            for chunk in response.iter_content():
                decoded_chunk = chunk.decode("utf-8")
                accumulated += decoded_chunk
                if accumulated.endswith("}"):
                    try:
                        json_chunk = json.loads(accumulated)
                        yield json_chunk
                        accumulated = ""
                    except json.JSONDecodeError:
                        pass

    def import_collection(self, collection: dict) -> None:
        """
        Import models from a folder into the database.
        :param collection: Collection parameters.
        """
        database_request = DatabaseRequest(
            method=DatabaseInteraction.put,
            object_type="collection",
            payload=collection
        )
        collection = self._send_request(database_request)["results"][0]
        self.cache["collection"][collection["uuid"]] = deepcopy(collection)

        imported_models = []
        for model_importer_key in collection["config"]["importer"]:
            imported_models.extend(
                self.cache["importer"][model_importer_key].import_models(root_path=collection["path"]))

        for model_params in imported_models:
            model_params["collection_uuid"] = collection["uuid"]
            database_request = DatabaseRequest(
                method=DatabaseInteraction.put,
                object_type="model",
                payload=model_params
            )
            model = self._send_request(database_request)["results"][0]
            self.cache["model"][model["uuid"]] = deepcopy(model)

    def interact_with_database(self, method: str, object_type: str, payload: dict | None = None) -> List[dict]:
        """
        Interacts with the backend database endpoint and returns raw results (no caching).
        :param method: Database interaction method.
        :param object_type: Target object type (e.g., "model", "collection").
        :param payload: Optional payload dictionary required by the selected method.
        :return: List of result dictionaries. Returns [] if the request fails or yields no results.
        """
        if method not in DatabaseInteraction.get_values():
            raise ValueError(
                f"Database interaction method '{method}' is not available, "
                f"choose from: {DatabaseInteraction.get_values()}")

        request = DatabaseRequest(
            method=method,
            object_type=object_type,
            payload=payload
        )
        results = self._send_request(request).get("results", [])

        if not results:
            return []
        for result in results:
            self.cache[object_type][result["uuid"]] = result
        return results
