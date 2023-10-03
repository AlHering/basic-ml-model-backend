# -*- coding: utf-8 -*-
"""
****************************************************
*                CommonFlaskFrontend                 
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, List
from flask import Blueprint
from src.utility.silver import environment_utility
from src.model.plugin_control.plugins import GenericPlugin
from src.model.plugin_control.exceptions import PluginImportException, PluginRuntimeException


class BlueprintPlugin(GenericPlugin):
    """
    BlueprintPlugin class, handling more complex tasks.
    """

    def __init__(self, info: dict, path: str, security_hash: str = None) -> None:
        """
        Representation of a BlueprintPlugin plugin, adding Blueprint pages to Flask websites.
        For more information on Blueprints, visit https://flask.palletsprojects.com/en/2.2.x/blueprints/.
        :param info: Plugin info.
        :param path: Path to plugin.
        :param security_hash: Hash that can be used for authentication purposes.
            Defaults to None.
        """
        super().__init__(info, path, security_hash)
        if "./" in self.info["blueprints"]:
            self.info["blueprints"] = os.path.normpath(
                os.path.join(path, self.info["blueprints"]))
        self.blueprints = environment_utility.get_module(
            self.info["blueprints"])
        if not hasattr(self.blueprints, "get_blueprints"):
            raise PluginImportException(
                self.name, self.type, "Plugin does not implement 'get_blueprints'-function correctly")
        if not hasattr(self.blueprints, "get_menu"):
            raise PluginImportException(
                self.name, self.type, "Plugin does not implement 'get_menu'-function correctly")

    def get_blueprints(self, *args, **kwargs) -> List[Blueprint]:
        """
        Method for getting blueprints.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: List of Blueprints.
        """
        return self.blueprints.get_blueprints(*args, **kwargs)

    def get_menu(self, *args, **kwargs) -> dict:
        """
        Method for getting menu dictionary.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        :return: Menu dictionary.
        """
        return self.blueprints.get_menu(*args, **kwargs)
