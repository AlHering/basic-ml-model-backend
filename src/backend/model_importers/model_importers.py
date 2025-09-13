# -*- coding: utf-8 -*-
import os
import re
from typing import List
from abc import ABC, abstractmethod
from src.utility.image_utility import IMAGE_EXTENSIONS


class ModelImporter(ABC):
    """
    Model Importer class.
    """

    def __init__(
            self,
            source: str,
            model_type: str,
            model_engine: str,
            structure_type: str,
            primary_regex: str,
            path_filters_include: List[str] = [],
            path_filters_exclude: List[str] = []) -> None:
        """
        Initiation method.
        :param source: Source tag like "civitai.com" or "huggingface.co".
        :param model_type: Arbitrary model type.
        :param model_engine: Arbitrary model engine.
        :param structure_type: Structure type from "single-file", "multi-file", "single-folder", or "multi-folder".
        :param primary_regex: Primary model file regex.
        :param path_filters_include: Parts that must be in file/folder paths.
        :param path_filters_exclude: Parts that must NOT be in file/folder paths.
        """
        self.source = source
        self.model_type = model_type
        self.model_engine = model_engine
        self.structure_type = structure_type
        self.path_filters_include = path_filters_include
        self.path_filters_exclude = path_filters_exclude
        self.primary_regex = primary_regex

    def _check_primary_filter(self, full_path: str) -> bool:
        """
        Checks primary model file for conditions.
        :param full_path: Full path to primary model file.
        :return: True, if conditions meet else False.
        """
        return (
            all(must_have in full_path for must_have in self.must_haves)
            and not any(must_not_have in full_path for must_not_have in self.must_not_haves)
            and re.fullmatch(self.primary_regex, full_path)
        )

    def _extract_model_name(self, full_path: str) -> str:
        """
        Extracts the name from the primary model file.
        :param full_path: Full path to primary model file.
        :return: Model name.
        """
        return (
            all(must_have in full_path for must_have in self.must_haves)
            and not any(must_not_have in full_path for must_not_have in self.must_not_haves)
            and re.fullmatch(self.primary_regex, full_path)
        )

    @abstractmethod
    def _extract_relevant_files(self, model_entry: dict) -> dict:
        """
        Extracts the relevant files.
        :param model_entry: Model entry.
        :return: Model files.
        """
        pass

    @abstractmethod
    def _calculate_size(self, model_entry: dict) -> str:
        """
        Extracts the name from the primary model file.
        :param model_entry: Model entry.
        :return: Model size.
        """
        pass

    def import_models(self, root_path: str) -> List[dict]:
        """
        Imports model from disk.
        :param root_path: Collection root path.
        :return: List of model entries.
        """
        imported_models = []
        for root, _, files in os.walk(root_path, topdown=True):
            for file in files:
                full_path = os.path.join(root, file)
                if self._check_primary_filter(full_path=full_path):
                    new_model = {
                        "model_type": self.model_type,
                        "engine": self.model_engine,
                        "source": self.source,
                        "name": self._extract_model_name(full_path),
                        "primary_file": file,
                        "path": root
                    }
                    new_model["files"] = self._extract_relevant_files(
                        model_entry=new_model)
                    new_model["size"] = self._calculate_size(
                        model_entry=new_model)
                    imported_models.append()


class CivitaiModelImporter(ModelImporter):
    """
    Civitai Importer class.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        super().__init__(
            source="civitai.com",
            model_type="image-gen",
            model_engine="comfyui",
            structure_type="multi-file",
            primary_regex="*",
            path_filters_include=[],
            path_filters_exclude=[]
        )
        self.gigabyte_divisor = (1024 ** 3)

    def _extract_relevant_files(self, model_entry: dict) -> dict:
        """
        Extracts the relevant files.
        :param model_entry: Model entry.
        :return: Model files.
        """
        file_name, file_ext = os.path.splitext(model_entry["primary_file"])
        path = model_entry["path"]
        relevant_files = {"primary": model_entry["primary_file"]}
        for rel_file in [file for file in os.listdir(
                path) if file.startswith(file_name)]:
            rel_file_name, rel_file_ext = os.path.splitext(rel_file)
            if rel_file_ext in IMAGE_EXTENSIONS:
                relevant_files["image"] = rel_file
            elif rel_file_ext == ".hash":
                relevant_files["hash"] = rel_file
            else:
                relevant_files[rel_file_name.split("_")[-1]] = rel_file
        return relevant_files

    def _calculate_size(self, model_entry: dict) -> str:
        """
        Extracts the name from the primary model file.
        :param model_entry: Model entry.
        :return: Model size.
        """
        return "{:.2f}GB".format(
            os.path.getsize(
                os.path.join(model_entry["path"],
                             model_entry["primary_file"])
            ) / self.gigabyte_divisor)
