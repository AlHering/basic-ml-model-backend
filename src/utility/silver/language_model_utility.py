# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility                      *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel


class LanguageModel(object):
    """
    Language model representation.
    """
    supported_types = {
        "llamacpp": {
            "loaders": {},
            "gateways": {}
        },
        "openai": {
            "loaders": {},
            "gateways": {}
        },
        "gpt4all": {
            "loaders": {},
            "gateways": {}
        },
        "bedrock": {
            "loaders": {},
            "gateways": {}
        },
        "cohere": {
            "loaders": {},
            "gateways": {}
        },
        "google_palm": {
            "loaders": {},
            "gateways": {}
        },
        "huggingface": {
            "loaders": {},
            "gateways": {}
        },
        "koboldai": {
            "loaders": {},
            "gateways": {}
        },
        "mosaicml": {
            "loaders": {},
            "gateways": {}
        },
        "replicate": {
            "loaders": {},
            "gateways": {}
        },
        "anthropic": {
            "loaders": {},
            "gateways": {}
        },
        "openllm": {
            "loaders": {},
            "gateways": {}
        },
        "openlm": {
            "loaders": {},
            "gateways": {}
        },
        "rwkv": {
            "loaders": {},
            "gateways": {}
        }

    }

    def __init__(self, representation: dict, *loader_args: Optional[Any], **loader_kwargs: Optional[Any]) -> None:
        """
        Initiation method.
        :param representation: Language model representation.
        :param loader_args: Loader arguments.
        :param loader_kwargs: Loader keyword arguments.
        """
        self.representation = representation
        self.instance = None
        self.instance_generate = None

        self._load_instance(*loader_args, **loader_kwargs)

    def _load_instance(self, *loader_args: Optional[Any], **loader_kwargs: Optional[Any]) -> None:
        """
        Internal method for loading instance.
        :param loader_args: Loader arguments.
        :param loader_kwargs: Loader keyword arguments.
        """
        if self.representation["type"] in self.supported_types:
            gateway = self.supported_types[self.representation["type"]]["gateways"].get(
                self.representation.get("gateway"))
            loader = self.supported_types[self.representation["type"]]["loaders"].get(
                self.representation["loader"])
            if gateway is not None:
                loader_args, loader_kwargs = gateway(
                    loader_args, loader_kwargs)
            self.instance = loader["instance"](*loader_args, **loader_kwargs)
            self.instance_generate = getattr(self.instance, loader["generate"])

    def generate(self, query: str) -> Optional[Any]:
        """
        Main handler method for wrapping language model capabilities.
        :param query: User query.
        :return: Response, if generation method is available else None.
        """
        return self.instance_generate(query) if self.instance_generate is not None else None


def spawn_language_model_instance(config: str) -> LanguageModel:
    """
    Function for spawning language model instance based on configuration.
    :param config: Instance configuration.
    :return: Language model instance.
    """
    pass
