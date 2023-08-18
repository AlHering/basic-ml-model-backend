# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import List, Any, Dict
from src.model.model_control.model_handler import GenericModelHandler
from src.model.model_control.api_wrapper import CivitaiAPIWrapper, HuggingfaceAPIWrapper
from src.model.model_control.model_database import ModelDatabase


class ModelController(object):
    """
    Class, representing ML Model Controller objects.
    A Model Controller manages Model Handlers, which use API Wrappers to provide
    model services for collecting metadata and downloading assets.
    """

    def __init__(self, handlers: Dict[str, GenericModelHandler] = None) -> None:
        """
        Initiation method.
        :param handlers: Handler dictionary.
            Defaults to None in which case only default handlers are initialized.
        """
        self.database = ModelDatabase(
            database_uri=None, schema="model_control")
        self.model_folder = None
        self.cache_path = None
        self.handlers = {} if handlers is None else handlers
        self._initiate_base_handlers()

    def _initiate_base_handlers(self) -> None:
        """
        Method for initiating base handlers.
        """
        for init_kwargs in [
            {
                "database": self.database,
                "model_folder": self.model_folder,
                "cache_path": self.cache_path,
                "apis": {"civitai": CivitaiAPIWrapper()},
                "sorting_field": "type",
                "sorters": ["BLIP", "BSRGAN", "CHECKPOINTS", "CODEFORMER",
                            "CONTROL_NET", "DEEPBOORU", "EMBEDDINGS", "ESRGAN",
                            "GFPGAN", "HYPERNETWORKS", "KARLO", "LDSR", "LORA",
                            "LYCORIS", "POSES", "REAL_ESRGAN", "SCUNET",
                            "STABLE_DIFFUSION", "SWINIR", "TEXTUAL_INVERSION",
                            "TORCH_DEEPDANBOORU", "VAE", "WILDCARDS"]
            },
            {
                "database": self.database,
                "model_folder": self.model_folder,
                "cache_path": self.cache_path,
                "apis": {"huggingface": HuggingfaceAPIWrapper()},
                "sorting_field": "task",
                "sorters": ["TEXT_GENERATION", "EMBEDDING", "LORA", "TEXT_CLASSIFICATION"]
            }
        ]:
            self.handlers.append(GenericModelHandler(**init_kwargs))

    def add_handler(self, handler: GenericModelHandler) -> None:
        """
        Method for adding handler.
        :param handler_class: Handler object.
        """
        self.handlers.append(handler)
