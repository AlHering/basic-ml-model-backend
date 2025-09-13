# -*- coding: utf-8 -*-
from __future__ import annotations
import os
from typing import Any
from enum import Enum
import json
import traceback
import uvicorn
from pydantic import BaseModel
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi import FastAPI, APIRouter
import asyncio
from queue import Empty
import traceback
from typing import List, Dict, Generator
import traceback
from datetime import datetime as dt
from uuid import UUID
from functools import wraps
import logging
from src.configuration import configuration as cfg
from src.database.basic_sqlalchemy_interface import BasicSQLAlchemyInterface, FilterMask
from src.database.data_model import populate_data_infrastructure, get_default_entries


BACKEND = FastAPI(title=cfg.PROJECT_NAME, version=cfg.PROJECT_VERSION,
                  description=cfg.PROJECT_DESCRIPTION)
INTERFACE: BackendServer | None = None
cfg.LOGGER = logging.getLogger("uvicorn.error")
cfg.LOGGER.setLevel(logging.DEBUG)


@BACKEND.get("/", include_in_schema=False)
async def root() -> dict:
    """
    Redirects to Swagger UI docs.
    :return: Redirect to Swagger UI docs.
    """
    return RedirectResponse(url="/docs")


def interaction_log(func: Any) -> Any | None:
    """
    Interaction logging decorator.
    :param func: Wrapped function.
    :return: Error report if operation failed, else function return.
    """
    @wraps(func)
    async def inner(*args: Any | None, **kwargs: Any | None):
        """
        Inner function wrapper.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        requested = dt.now()
        try:
            response = await func(*args, **kwargs)
        except Exception as ex:
            response = {
                "status": "error",
                "exception": str(ex),
                "trace": traceback.format_exc()
            }
        responded = dt.now()
        log_data = {
            "request": {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            },
            "response": json.dumps(response) if isinstance(response, dict) else str(response),
            "requested": requested,
            "responded": responded
        }
        args[0].database.post_object(
            object_type="log",
            **log_data
        )
        logging_message = f"Interaction with {args[0]}: {log_data}"
        logging.info(logging_message)
        return response
    return inner


class DatabaseInteraction(str, Enum):
    """
    Database interaction methods.
    """
    get_all = "get_all"
    get = "get"
    put = "put"
    patch = "patch"
    delete = "delete"

    def __str__(self) -> str:
        """
        Returns string representation.
        """
        return str(self.value)

    @classmethod
    def get_values(cls) -> List[str]:
        """
        Returns values.
        :return: List of values.
        """
        return [value for value in cls._value2member_map_]


class DatabaseRequest(BaseModel):
    """Database interaction request class."""
    method: DatabaseInteraction
    object_type: str
    payload: dict | None = None


class BaseRequest(BaseModel):
    """Service request class."""
    service: str
    input_package: dict
    timeout: float | None = None


class BaseResponse(BaseModel):
    """Config payload class."""
    status: str
    results: List[dict]
    metadata: dict | None = None


class Endpoints(str, Enum):
    """
    Endpoints config.
    """
    status = "status"
    database_interaction = "database-interaction"

    def __str__(self) -> str:
        """
        Returns string representation.
        """
        return str(self.value)

    @classmethod
    def get_values(cls) -> List[str]:
        """
        Returns values.
        :return: List of values.
        """
        return [value for value in cls._value2member_map_]


class BackendServer(object):
    """
    Backend registry.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        :param services: Services.
        """
        workdir = os.path.join(cfg.PATHS.DATA_PATH, "backend")
        os.makedirs(workdir, exist_ok=True)
        self.database = BasicSQLAlchemyInterface(
            working_directory=workdir,
            population_function=populate_data_infrastructure,
            default_entries=get_default_entries()
        )
        self.router: APIRouter | None = None

    def setup_router(self) -> APIRouter:
        """
        Sets up an API router.
        :return: API router.
        """

        return self.router

    def setup_router(self) -> APIRouter:
        """
        Sets up an API router.
        :return: API router.
        """
        self.router = APIRouter(prefix=cfg.BACKEND_ENDPOINT_BASE)
        self.router.add_api_route(
            path=f"/{Endpoints.status}",
            endpoint=self.status,
            methods=["GET"]
        )
        self.router.add_api_route(
            path=f"/{Endpoints.database_interaction}",
            endpoint=self.interact_with_database,
            methods=["POST"]
        )

        return self.router

    """
    Service interaction
    """
    @interaction_log
    async def status(self) -> BaseResponse:
        """
        Get backend status.
        """
        return BaseResponse(status="success", results=[])

    def stream(self, base_request: BaseRequest) -> Generator[bytes, None, None]:
        """
        Runs a service process.
        :param base_request: Base request.
        :return: Base response generator.
        """
        # yield json.dumps(response.model_dump()).encode("utf-8")
        yield None

    @interaction_log
    async def process_as_stream(self, base_request: BaseRequest) -> StreamingResponse:
        """
        Runs a service process in streamed mode.
        :param base_request: Base request.
        :return: Base response.
        """
        return StreamingResponse(self.stream(service_request=base_request), media_type="text/plain")

    def respond_error(self, ex: Any) -> BaseResponse:
        """
        Returns exception response.
        :param ex: Exception.
        :return: Base response.
        """
        return BaseResponse(
            status="error",
            results=[{"error": str(ex),
                      "trace": traceback.format_exc()}]
        )

    """
    ORM interaction methods
    """

    @interaction_log
    async def interact_with_database(self, database_request: DatabaseRequest) -> BaseResponse:
        """
        Interacts with database.
        :param database_request: Database request.
        :return: Base response.
        """
        supported_methods = DatabaseInteraction.get_values()
        method = database_request.method
        object_type = database_request.object_type
        payload = database_request.payload
        if payload and "uuid" in payload:
            payload["uuid"] = UUID(payload["uuid"])

        try:
            if method not in supported_methods:
                raise ValueError(
                    f"Database interaction method '{method}' is not availabile, choose from: {supported_methods}")
            elif object_type not in self.database.model:
                raise ValueError(
                    f"Object type '{object_type}' is not handled through database, choose from: {[key for key in self.database.model if key != 'log']}")
            elif method == "get_all":
                objects = self.database.get_objects_by_type(
                    object_type=object_type)
                return BaseResponse(
                    status="success",
                    results=[self.database.obj_as_dict(
                        objects, convert_timestamps=True, convert_uuids=True) for obj in objects],
                    metadata={"count": len(objects)}
                )
            elif method == "get":
                obj = self.database.get_object_by_id(
                    object_type=object_type, object_id=payload[self.database.primary_keys[object_type]])
                return BaseResponse(
                    status="success",
                    results=[self.database.obj_as_dict(
                        obj, convert_timestamps=True, convert_uuids=True)],
                    metadata={"count": 1 if obj else 0}
                )
            elif method == "put":
                return BaseResponse(
                    status="success",
                    results=[self.database.obj_as_dict(
                        self.database.put_object(object_type=object_type, object_attributes=None, **payload), convert_timestamps=True, convert_uuids=True)],
                    metadata={"count": 1}
                )
            elif method == "patch":
                object_id = payload.pop(
                    self.database.primary_keys[object_type])
                return BaseResponse(
                    status="success",
                    results=[self.database.obj_as_dict(
                        self.database.patch_object(object_type=object_type, object_id=object_id, **payload), convert_timestamps=True, convert_uuids=True)],
                    metadata={"count": 1}
                )
            elif method == "delete":
                object_id = payload.pop(
                    self.database.primary_keys[object_type])
                return BaseResponse(
                    status="success",
                    results=[self.database.obj_as_dict(
                        self.database.delete_object(object_type=object_type, object_id=object_id, **payload), convert_timestamps=True, convert_uuids=True)],
                    metadata={"count": 1}
                )
        except Exception as ex:
            return BaseResponse(
                status="error",
                results=[{"error": str(ex),
                          "trace": traceback.format_exc()}]
            )


"""
Backend server
"""


def run() -> None:
    """
    Runs backend server.
    """
    global BACKEND, INTERFACE
    INTERFACE = BackendServer()
    BACKEND.include_router(INTERFACE.setup_router())
    uvicorn.run("src.backend.backend_server:BACKEND",
                host=cfg.BACKEND_HOST,
                port=cfg.BACKEND_PORT,
                log_level="debug")


if __name__ == "__main__":
    run()
