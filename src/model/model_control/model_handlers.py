# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional, List, Tuple
import abc
from src.configuration import configuration as cfg
import os
from src.utility.bronze import json_utility, hashing_utility, dictionary_utility
from src.model.model_control.model_database import ModelDatabase


class AbstractModelHandler(object):
    """
    Class, representing ML Model Handler objects.
    A Model Handler utilizes API Wrappers for collecting metadata and downloading assets from
    model services and managing updates, organization and usage.
    """

    def __init__(self, db_interface: ModelDatabase, api_wrapper_dict: dict, cache: dict = None) -> None:
        """
        Initiation method.
        :param db_interface: Model database.
        :param api_wrapper_dict: Dictionary, mapping source to API wrapper.
        :param cache: Cache to initialize handler with.
            Defaults to None in which case an empty cache is created.
        """
        self._logger = cfg.Logger
        self._db = db_interface
        self._apis = api_wrapper_dict
        self._cache = cache if cache is not None else {}

    def import_cache(self, import_path: str) -> None:
        """
        Method for importing cache data.
        :param import_path: Import path.
        """
        self._logger.log(f"Importing cache from '{import_path}'...")
        self._cache = json_utility.load(import_path)

    def export_cache(self, export_path: str) -> None:
        """
        Method for exporting cache data.
        :param export_path: Export path.
        """
        self._logger.log(f"Exporting cache to '{export_path}'...")
        json_utility.save(self._cache, export_path)

    @abc.abstractmethod
    def load_model_folder(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for loading model folder.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    @abc.abstractmethod
    def link_model_file(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for linking model files.
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
    def organize_models(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Abstract method for organizing local models.
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


class StabeDiffusionModelHandler(AbstractModelHandler):
    """
    Class, representing Model Handler for Stable Diffusion models.
    """

    def __init__(self, db_interface: ModelDatabase, api_wrapper_dict: dict) -> None:
        """
        Initiation method.
        :param db_interface: Model database.
        :param api_wrapper_dict: Dictionary, mapping source to API wrapper.
        """
        super().__init__(db_interface, api_wrapper_dict)
        self._logger = cfg.LOGGER

    def load_model_folder(self, model_folder: str, ignored_sub_folders: List[str] = [], ignored_model_files: List[str] = []) -> None:
        """
        Method for loading model folder.
        :param model_folder: Model folder to load.
        :param ignored_sub_folders: Subfolder parts to ignore.  
            Defaults to an empty list.
        :param ignored_model_files: Model files to ignore.  
            Defaults to an empty list.
        """
        self._logger.info(f"Loading model folders under '{model_folder}'...")
        already_tracked_files = self._db.get_tracked_model_files(
            model_folder, ignored_sub_folders, ignored_model_files)
        self._logger.info(
            f"Found {len(already_tracked_files)} already tracked files...")

        for root, _, files in os.walk(model_folder, topdown=True):
            self._logger.info(f"Checking '{root}'...")

            if any(subfolder in ignored_sub_folders for subfolder in root.replace(
                    model_folder, "").split("/")):
                self._logger.info(f"Ignoring '{root}'.")
            else:
                for model_file in self.extract_model_files(files):
                    self._logger.info(f"Found '{model_file}'.")
                    full_model_path = os.path.join(root, model_file)
                    if not any(os.path.join(model.folder, model.file_name) == full_model_path for model in already_tracked_files):
                        if model_file not in ignored_model_files:
                            self._logger.info(
                                f"'{model_file}' is not tracked, collecting data...")

                            data = {
                                "file_name": model_file,
                                "folder": root,
                                "sha256": hashing_utility.hash_with_sha256(os.path.join(root, model_file))
                            }
                            self._db._post(
                                "model_file", self._db.model["model_file"](**data))

                        else:
                            self._logger.info(f"Ignoring '{model_file}'.")
                    else:
                        self._logger.info(
                            f"'{model_file}' is already tracked.")

    def link_model_file(self, files: List[str] = None) -> None:
        """
        Method for linking model files.
        :param files: Files to link.
            Defaults to None, in which case all unknown models are linked.
        """
        for unkown_model in self._db.get_unlinked_model_files(files):
            linkage = self.calculate_linkage(unkown_model)
            if linkage is not None:
                self._db.link_model_file(unkown_model, {
                    "source": linkage[0],
                    "api_url": linkage[1],
                    "metadata": linkage[2]
                })

    def calculate_linkage(self, model_file: Any) -> Optional[Tuple[str, str, dict]]:
        """
        Method for calculating source linkage.
        :param model_file: Model file object.
        :return: Tuple of source and API URL and metadata if found else None.
        """
        for possible_source in self._apis:
            metadata = self._apis[possible_source].collect_metadata(
                "hash", model_file.sha256)
            if metadata:
                return possible_source, self._apis[possible_source].get_api_url("hash", model_file.sha256), self._apis[possible_source].normalize_metadata(metadata)
        return None

    def update_metadata(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for updating cached metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def organize_models(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for organizing local models.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass

    def move_model(self, *args: Optional[List], **kwargs: Optional[dict]) -> None:
        """
        Method for moving local model and adjusting metadata.
        :param args: Arbitrary arguments.
        :param kwargs: Arbitrary keyword arguments.
        """
        pass
