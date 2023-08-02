# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import uvicorn
import os
from enum import Enum
from typing import Union, List, Optional, Any, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from functools import wraps
from src.configuration import configuration as cfg
from src.control.backend_controller import BackendController

"""
Backend control
"""
BACKEND = FastAPI(title="Basic Language Model Backend", version="0.1",
                  description="Backend for serving Language Model capabilities.")
STATUS = False
CONTROLLER: BackendController = None


def access_validator(status: bool) -> Optional[Any]:
    """
    Validation decorator.
    :param func: Decorated function.
    :param status: Status to check.
    :return: Error message if status is incorrect, else function return.
    """
    global STATUS

    def wrapper(func: Any) -> Optional[Any]:
        """
        Function wrapper.
        :param func: Wrapped function.
        :return: Error message if status is incorrect, else function return.
        """
        @wraps(func)
        async def inner(*args: Optional[Any], **kwargs: Optional[Any]):
            """
            Inner function wrapper.
            :param args: Arguments.
            :param kwargs: Keyword arguments.
            """
            if status != STATUS:
                return {"message": f"System is {' already started' if STATUS else 'currently stopped'}"}
            else:
                return await func(*args, **kwargs)
        return inner
    return wrapper


"""
Dataclasses
"""


class Model(BaseModel):
    """
    Dataclass for model representation.
    """
    uuid: str
    path: str
    type: str
    loader: str


"""
BACKEND ENDPOINTS
"""


class Endpoints(str, Enum):
    """
    String-based endpoint enum class.
    """
    BASE = "/api/v1"

    GET_MODELS = f"{BASE}/models/"
    GET_MODEL = f"{BASE}/model/"
    POST_MODEL = f"{BASE}/model/"
    PATCH_MODEL = f"{BASE}/model/{{model_uuid}}"
    DELETE_MODEL = f"{BASE}/model/{{model_uuid}}"

    POST_CONFIGURE_INSTANCE = f"{BASE}/instance/configure"
    POST_LOAD_INSTANCE = f"{BASE}/instance/{{instance_uuid}}/load"
    POST_UNLOAD_INSTANCE =  f"{BASE}/instance/{{instance_uuid}}/unload"

    POST_GENERATE = f"{BASE}/instance/{{instance_uuid}}/generate"

    def __str__(self) -> str:
        """
        Getter method for a string representation.
        """
        return self.value


"""
Basic backend endpoints
"""


@BACKEND.get(Endpoints.GET_STATUS)
async def get_status() -> dict:
    """
    Root endpoint for getting system status.
    :return: Response.
    """
    global STATUS
    return {"message": f"System is {'started' if STATUS else 'stopped'}!"}


@BACKEND.post(Endpoints.POST_START)
@access_validator(status=False)
async def post_start() -> dict:
    """
    Endpoint for starting system.
    :return: Response.
    """
    global STATUS
    global CONTROLLER
    CONTROLLER = BackendController()
    STATUS = True
    return {"message": f"System started!"}


@BACKEND.post(Endpoints.POST_STOP)
@access_validator(status=True)
async def post_stop() -> dict:
    """
    Endpoint for stopping system.
    :return: Response.
    """
    global STATUS
    global CONTROLLER
    CONTROLLER.shutdown()
    STATUS = False
    return {"message": f"System stopped!"}


"""
Models endpoints
"""


@BACKEND.get(Endpoints.GET_MODELS)
@access_validator(status=True)
async def get_models() -> dict:
    """
    Endpoint for getting models.
    :return: Response.
    """
    global CONTROLLER
    return {"models": CONTROLLER.get_objects("model")}


@BACKEND.get(Endpoints.GET_MODEL)
@access_validator(status=True)
async def get_model(model_uuid: str) -> dict:
    """
    Endpoint for getting a specific model.
    :param model_uuid: Model UUID.
    :return: Response.
    """
    global CONTROLLER
    return {"models": CONTROLLER.get_object("model", model_uuid)}


@BACKEND.post(Endpoints.POST_MODEL)
@access_validator(status=True)
async def post_model(model: Model) -> dict:
    """
    Endpoint for posting a model.
    :param model: Model.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("model",
                                           **model.dict())}


@BACKEND.patch(Endpoints.PATCH_MODEL)
@access_validator(status=True)
async def patch_model(model_uuid: str, model: Model) -> dict:
    """
    Endpoint for patching a model.
    :param model_uuid: Model UUID.
    :param model: Model.
    :return: Response.
    """
    return {"uuid": CONTROLLER.patch_object("model",
                                            model_uuid,
                                            **model.dict())}


@BACKEND.delete(Endpoints.DELETE_MODEL)
@access_validator(status=True)
async def delete_model(model_uuid: str) -> dict:
    """
    Endpoint for deleting a model.
    :param model_uuid: Model UUID.
    :return: Response.
    """
    return {"uuid": CONTROLLER.delete_object("model",
                                             model_uuid)}


@BACKEND.post(Endpoints.POST_CONFIGURE_INSTANCE)
@access_validator(status=True)
async def post_configure(config: dict) -> dict:
    """
    Endpoint for configuring a model.
    :param config: Config.
    :return: Response.
    """
    return {"uuid": CONTROLLER.post_object("config",
                                           config)}

@BACKEND.post(Endpoints.POST_LOAD_INSTANCE)
@access_validator(status=True)
async def load_instance(config_uuid: str) -> dict:
    """
    Endpoint for loading a model instance.
    :param config_uuid: Config UUID.
    :return: Response.
    """
    pass

@BACKEND.post(Endpoints.POST_UNLOAD_CONTROLLER)
@access_validator(status=True)
async def unload_instance(instance_uuid: str) -> dict:
    """
    Endpoint for unloading a model instance.
    :param instance_uuid: Instance UUID.
    :return: Response.
    """
    pass


"""
Backend runner
"""


def run_backend(host: str = None, port: int = None, reload: bool = True) -> None:
    """
    Function for running backend server.
    :param host: Server host. Defaults to None in which case "127.0.0.1" is set.
    :param port: Server port. Defaults to None in which case either environment variable "BACKEND_PORT" is set or 7861.
    :param reload: Reload flag for server. Defaults to True.
    """
    uvicorn.run("src.interfaces.backend_interface:BACKEND",
                host="127.0.0.1" if host is None else host,
                port=int(
                    cfg.ENV.get("BACKEND_PORT", 7861) if port is None else port),
                reload=True)


if __name__ == "__main__":
    run_backend()
