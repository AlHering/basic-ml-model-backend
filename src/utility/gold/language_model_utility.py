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
Loader classes
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
        self.llm = LlamaCpp(

        ).generate()

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


def spawn_language_model_instance(config: str) -> LanguageModel:
    """
    Function for spawning language model instance based on configuration.
    :param config: Instance configuration.
    :return: Language model instance.
    """
    pass
