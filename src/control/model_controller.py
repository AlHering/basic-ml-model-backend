# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List, Any
from src.model.model_control.model_handlers import GenericModelHandler
from src.model.model_control.model_database import ModelDatabase


class ModelController(object):
    """
    Class, representing ML Model Controller objects.
    A Model Controller manages Model Handlers, which use API Wrappers to provide
    model services for collecting metadata and downloading assets.
    """

    def __init__(self, handlers: List[GenericModelHandler] = None) -> None:
        """
        Initiation method.
        """
        self.database = ModelDatabase(
            database_uri=None, schema="model_control")
        self.handlers = [] if handlers is None else handlers

    def add_handler(self, handler: GenericModelHandler) -> None:
        """
        Method for adding handler.
        :param handler_class: Handler object.
        """
        self.handlers.append(handler)
