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
from langchain.llms import LlamaCpp

"""
Wrapper classes
"""


class LlamaCppWrapper(object):
    """
    Wrapper class for LlamaCpp.
    """

    def __init__(self, representation: dict) -> None:
        """
        Initiation method.
        :param representation: Language model representation.
        """
        self.llm = LlamaCpp().generate()

    def generate(self, query: str) -> Optional[Any]:
        """
        Generation method.
        :param query: User query.
        :return: Response, if generation method is available else None.
        """
        return self.llm.generate([query])


"""
Parameter gateways
"""


"""
Parameterized Language Models
"""


class LanguageModel(object):
    """
    Language model representation.
    """
    supported_types = {
        "llamacpp": {
            "loaders": {
                "_default": LlamaCppWrapper
            },
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

    def __init__(self, representation: dict) -> None:
        """
        Initiation method.
        :param representation: Language model representation.
        """
        self.representation = representation
        self.instance = None
        self.instance_generate = None

        self._load_instance()

    def _load_instance(self,) -> None:
        """
        Internal method for loading instance.
        """
        if self.representation["type"] in self.supported_types:
            gateway = self.supported_types[self.representation["type"]]["gateways"].get(
                self.representation.get("gateway", "_default"))
            loader = self.supported_types[self.representation["type"]]["loaders"].get(
                self.representation.get("loader", "_default"))
            if gateway is not None:
                loader_args, loader_kwargs = gateway(self.representation)
            if loader:
                self.instance = loader["instance"](
                    *loader_args, **loader_kwargs)
                self.instance_generate = getattr(
                    self.instance, loader["generate"])

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
