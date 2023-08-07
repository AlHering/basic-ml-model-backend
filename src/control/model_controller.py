# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List, Any
from src.model.model_control.model_handlers import StabeDiffusionModelHandler
from src.interfaces.model_database import ModelDatabase


class ModelController(object):
    """
    Class, representing ML Model Controller objects.
    A Model Controller manages Model Handlers, which use API Wrappers to
    model services for collecting metadata and downloading assets.
    """

    def __init__(self, handlers: List[dict] = None) -> None:
        """
        Initiation method.
        :param handlers: List of handlers as dictionaries of the form
            {
                "handler_type": <Handler Type>,
                "db_interface": <ModelDatabase>,
                "api_wrapper_dict": <API-Wrapper-dict>,
                "cache": <Cache>
            }
            Defaults to None in which case the controller awaits new handlers to be added.
        """
        self.handler_classes = {
            "stablediffusion": StabeDiffusionModelHandler
        }
        self.handlers = [self.handler_classes[entry["handler_type"]](
            entry["db_interface"], entry["api_wrapper_dict"], entry.get("cache")) for entry in handlers]

    def add_handler(self, db_interface: ModelDatabase, handler_type: Any, api_wrapper_dict, cache: dict = None) -> None:
        """
        Method for adding handler.
        :param handler_class: Handler class for initiating handler.
        """
        self.handlers.append(self.handler_classes[handler_type](
            db_interface, api_wrapper_dict, cache))

    def _integrate_into_frontend() -> None:
        """
        Internal method for integrating Model Controller functionality into Common Flask Frontend.
        """
        pass
