# -*- coding: utf-8 -*-
"""
****************************************************
*                     Utility                      *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any
from abc import ABC, abstractmethod


class LanguageModel(ABC):
    """
    Abstract language model class.
    """

    @abstractmethod
    def handle_query(query: str) -> Any:
        """
        Main handler method for wrapping language model capabilities.
        :param query: User query.
        :return: Response.
        """
        pass


def spawn_language_model_instance(config: str) -> LanguageModel:
    """
    Function for spawning language model instance based on configuration.
    :param config: Instance configuration.
    :return: Language model instance.
    """
    pass
