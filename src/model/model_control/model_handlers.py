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


class GenericModelHandler(object):
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

    def download_assets(self, target_type: str, target_id: int) -> None:
        """
        Method for downloading assets for target.
        :param target_type: Target object type.
        :param target_id: Target ID.
        """
        obj, wrapper = self.get_object_and_wrapper(target_type, target_id)
        if obj is not None and wrapper is not None:
            self.apis[wrapper].download_asset(obj)

    def download_modelversion(self, modelversion_id: int) -> None:
        """
        Method for downloading a model.
        :param modelversion_id: Modelversion ID.
        """
        obj, wrapper = self.get_object_and_wrapper(
            "modelversion", modelversion_id)
        if obj is not None and wrapper is not None:
            self.apis[wrapper].download_modelversion(obj)

    def get_object_and_wrapper(self, target_type: str, target_id: int) -> Tuple[Any, str]:
        """
        Method for downloading assets for target.
        :param target_type: Target object type.
        :param target_id: Target ID.
        :return: Target object and API wrapper.
        """
        obj = None
        wrapper = None

        obj = self.database.get_object_by_id(target_type, target_id)
        if obj is not None and obj.url is None:
            if target_type == "model":
                self.link_model(target_id)
            elif target_type == "modelversion":
                self.link_modelversion(target_id)
            obj = self.database.get_object_by_id(target_type, target_id)

        if obj is not None and obj.url is not None:
            wrapper = self.get_api_wrapper_for_url(obj.url)

        return obj, wrapper

    def link_model(self, model_id: int, api_wrapper_name: str = None) -> None:
        """
        Method for linking model entries.
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

    def link_modelversion(self, modelversion_id: int, api_wrapper_name: str = None) -> None:
        """
        Method for linking model version entries.
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

    def update_metadata(self, target_type: str, target_id: int) -> None:
        """
        Method for updating metadata.
        :param target_type: Target object type.
        :param target_id: Target ID.
        """
        obj, wrapper = self.get_object_and_wrapper(target_type, target_id)
        if obj is not None:
            if obj.url is None:
                if target_type == "model":
                    self.link_model(target_id)
                elif target_type == "modelversion":
                    self.link_modelversion(target_id)
                obj = self.database.get_object_by_id(target_type, target_id)

        if obj.url is not None and wrapper is not None:
            metadata = self.apis[wrapper].collect_metadata(obj)
            if metadata is not None:
                self.database.patch_object(
                    target_type, target_id, meta_data=metadata)

    def create_model_folder(self, model_id: int, api_wrapper_name: str = None) -> None:
        """
        Method for creating a model folder.
        :param model_id: Model ID.
        :param api_wrapper_name: Name of API wrapper to use.   
            Defaults to None in which case all APIs are tested.
        """
        obj, wrapper = self.get_object_and_wrapper("model", model_id)
        if api_wrapper_name is not None:
            wrapper = api_wrapper_name
        if obj:
            if not os.path.exists(obj.path):
                os.makedirs(obj.path)
        if wrapper is not None:
            self.apis[wrapper].download_model(obj)

    def get_api_wrapper_for_url(self, url: str) -> Optional[str]:
        """
        Abstract method for getting API wrapper to handle URL.
        :param url: URL to get wrapper for.
        :return: Appropriate API wrapper name.
        """
        for wrapper in self.apis:
            if self.apis[wrapper].validate_url_responsiblity(url):
                return wrapper

    @abc.abstractmethod
    def load_model_folder(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for loading model folder.
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


class LanguageModelHandler(GenericModelHandler):
    """
    Class, representing Model Handler for language models.
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
        super().__init__(database, model_folder, cache_path, apis, [
            "TEXT_GENERATION", "EMBEDDING", "LORA", "TEXT_CLASSIFICATION"] if tasks is None else tasks)

    # Override
    def load_model_folder(self) -> None:
        """
        Method for loading model folder.
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
