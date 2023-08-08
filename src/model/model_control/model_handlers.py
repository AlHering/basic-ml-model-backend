# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from typing import Any, Optional, List, Tuple, Dict
import abc
from src.configuration import configuration as cfg
from src.utility.bronze import json_utility, hashing_utility, dictionary_utility
from src.utility.silver import file_system_utility
from src.utility.gold.filter_mask import FilterMask
from src.model.model_control.api_wrappers import AbstractAPIWrapper
from src.model.model_control.model_database import ModelDatabase


class AbstractModelHandler(object):
    """
    Class, representing ML Model Handler objects.
    A Model Handler utilizes API Wrappers for collecting metadata and downloading assets from
    model services and managing updates, organization and usage.
    """

    def __init__(self, database: ModelDatabase, model_folder: str, cache_path: str, apis: Dict[str, AbstractAPIWrapper] = None, tasks: List[str] = None) -> None:
        """
        Initiation method.
        :param database: Database for model data.
        :param model_folder: Model folder under which the handlers models are kept.
        :param cache_path: Cache path for handler.
        :param apis: API wrappers.
        :param tasks: Model tasks.
        """
        self._logger = cfg.Logger
        self.database = database
        self.model_folder = model_folder
        self.cache_path = cache_path
        self.apis = [] if apis is None else apis
        self.tasks = [] if tasks is None else tasks
        self._cache = {}
        if os.path.exists(self.cache_path):
            self.import_cache()

    def import_cache(self, import_path: str = None) -> None:
        """
        Method for importing cache data.
        :param import_path: Import path.
            Defaults to handler's cache path.
        """
        import_path = self.cache_path if import_path is None else import_path
        self._logger.log(f"Importing cache from '{import_path}'...")
        self._cache = json_utility.load(import_path)

    def export_cache(self, export_path: str) -> None:
        """
        Method for exporting cache data.
        :param export_path: Export path.
            Defaults to handler's cache path.
        """
        export_path = self.cache_path if export_path is None else export_path
        self._logger.log(f"Exporting cache to '{export_path}'...")
        json_utility.save(self._cache, export_path)

    def get_unlinked_models(self, task: str = None) -> List[Any]:
        """
        Method for acquiring unlinked models.
        :param task: Task constraint.
            Defaults to None.
        """
        filtermask_expressions = [["url", "==", None]]
        if task is not None:
            filtermask_expressions.append(["task", "==", task])
        return self.database.get_objects_by_filtermasks(
            "model",
            [FilterMask(filtermask_expressions)]
        )

    def get_unlinked_modelversions(self) -> List[Any]:
        """
        Method for acquiring unlinked modelversions.
        """
        return self.database.get_objects_by_filtermasks(
            "model",
            [FilterMask([["url", "==", None]])]
        )

    @abc.abstractmethod
    def load_model_folder(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for loading model folder.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def link_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for linking model.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def link_modelversion(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for linking model version.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def update_metadata(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for updating cached metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def download_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for downloading a model.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def scrape_available_models(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for scraping available models.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def move_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for moving local model and adjusting metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass


class TextgenerationModelHandler(AbstractModelHandler):
    """
    Class, representing Model Handler for text generation models.
    """

    def __init__(self, database: ModelDatabase, model_folder: str, cache_path: str, apis: Dict[str, AbstractAPIWrapper] = None, tasks: List[str] = None) -> None:
        """
        Initiation method.
        :param database: Database for model data.
        :param model_folder: Model folder under which the handlers models are kept.
        :param cache_path: Cache path for handler.
        :param apis: API wrappers.
        :param tasks: Model tasks.
        """
        super().__init__(database, model_folder, cache_path, apis, tasks)

    def load_model_folder(self) -> None:
        """
        Abstract method for loading model folder.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        possible_tasks = file_system_utility.get_all_folders(
            self.model_folder)
        self.tasks.extend(
            [folder for folder in possible_tasks if folder not in self.tasks])
        for task in self.tasks:
            index_path = os.path.join(
                self.model_folder, task, "model_index.json")
            index = None
            if os.path.exists(index_path):
                index = json_utility.load(index_path)
            for folder in (file_system_utility.get_all_folders(
                    os.path.join(self.model_folder, task), include_root=False)):
                if not self.database.get_objects_by_filtermasks(
                    "model",
                    [FilterMask([["path", "==", folder], ["task", "==", task]])]
                ):
                    self.database.post_object("model", {
                        "path": folder,
                        "task": task
                    } if index is None or folder not in index else index[folder])

    # Override
    def link_model(self, model_id: int, api_wrapper_name: str = None) -> None:
        """
        Abstract method for linking model files.
        :param model_id: Model ID.
        :param api_wrapper_name: Name of API wrapper to use.   
            Defaults to None in which case all APIs are tested.
        """
        model = self.database.get_object_by_id("model", model_id)
        wrapper_options = list(self.apis.keys()) if api_wrapper_name is None else [
            api_wrapper_name]
        for api_wrapper in wrapper_options:
            result = self.apis[api_wrapper].get_model_page(model)
            if result is not None:
                self.database.patch_object("model", model_id, url=result)
                break

    # Override
    def link_modelversion(self, modelversion_id: int, api_wrapper_name: str = None) -> None:
        """
        Abstract method for linking model files.
        :param model_id: Model ID.
        :param api_wrapper_name: Name of API wrapper to use.
            Defaults to None in which case all APIs are tested.
        """
        modelversion = self.database.get_object_by_id(
            "modelversion", modelversion_id)
        wrapper_options = list(self.apis.keys()) if api_wrapper_name is None else [
            api_wrapper_name]
        for api_wrapper in wrapper_options:
            result = self.apis[api_wrapper].get_api_url(modelversion)
            if result is not None:
                self.database.patch_object(
                    "modelversion", modelversion_id, url=result)
                break
