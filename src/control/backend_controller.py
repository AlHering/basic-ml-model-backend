# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from uuid import UUID
from time import sleep
from datetime import datetime as dt
from typing import Optional, Any, List
from src.configuration import configuration as cfg
from src.model.backend_control.llm_pool import ThreadedLLMPool
from src.model.backend_control.dataclasses import create_or_load_database


class BackendController(object):
    """
    Controller class for handling backend interface requests.
    """

    def __init__(self, working_directory: str = None) -> None:
        """
        Initiation method.
        :param working_directory: Working directory.
            Defaults to folder 'processes' folder under standard backend data path.
        """
        self.working_directory = os.path.join(cfg.PATHS.BACKEND_PATH, "processes"
                                              ) if working_directory is None else working_directory
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        self.database_uri = cfg.ENV.get(
            "BACKEND_DATABASE", f"sqlite:///{self.working_directory}/backend.db")
        # TODO: Add typing gateway to dataclass handling -> UUIDs with '-' are not parsed correctly
        representation = create_or_load_database(self.database_uri)
        self.base = representation["base"]
        self.engine = representation["engine"]
        self.model = representation["model"]
        self.session_factory = representation["session_factory"]
        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        # TODO: Include priority and interrupt system when implemented in LLMPool class.
        self._cache = {}
        self.llm_pool = ThreadedLLMPool()

    def shutdown(self) -> None:
        """
        Method for running shutdown process.
        """
        self.llm_pool.stop_all()
        while any(self.llm_pool.is_running(instance_uuid) for instance_uuid in self._cache):
            sleep(2.0)

    def load_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for loading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Instance UUID if process as successful.
        """
        if instance_uuid in self._cache:
            if not self.llm_pool.is_running(instance_uuid):
                self.llm_pool.load_llm(instance_uuid)
                self._cache[instance_uuid]["restarted"] += 1
        else:
            self._cache[instance_uuid] = {
                "started": None,
                "restarted": 0,
                "accessed": 0,
                "inactive": 0
            }
            self.llm_pool.prepare_llm(self.get_object(
                "instance", UUID(instance_uuid)).config, instance_uuid)
            self.llm_pool.load_llm(instance_uuid)
            self._cache[instance_uuid]["started"] = dt.now()
        return instance_uuid

    def unload_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for unloading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Instance UUID if process as successful.
        """
        if instance_uuid in self._cache:
            if self.llm_pool.is_running(instance_uuid):
                self.llm_pool.unload_llm(instance_uuid)
            return instance_uuid
        else:
            return None

    def forward_generate(self, instance_uuid: str, prompt: str) -> Optional[str]:
        """
        Method for forwarding a generate request to an instance.
        :param instance_uuid: Instance UUID.
        :param prompt: Prompt.
        :return: Instance UUID.
        """
        self.load_instance(instance_uuid)
        return self.llm_pool.generate(instance_uuid, prompt)

    """
    Default object interaction.
    """

    def get_objects(self, object_type: str) -> List[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :return: List of objects of given type.
        """
        return self.session_factory().query(self.model[object_type]).all()

    def get_object(self, object_type: str, object_id: Any) -> Optional[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :return: An object of given type and ID, if found.
        """
        return self.session_factory().query(self.model[object_type]).filter(
            getattr(self.model[object_type],
                    self.primary_keys[object_type]) == object_id
        ).first()

    def post_object(self, object_type: str, **object_attributes: Optional[Any]) -> Optional[Any]:
        """
        Method for adding an object.
        :param object_type: Target object type.
        :param object_attributes: Object attributes.
        :return: Object ID of added object, if adding was successful.
        """
        obj = self.model[object_type](**object_attributes)
        with self.session_factory() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return getattr(obj, self.primary_keys[object_type])

    def patch_object(self, object_type: str, object_id: Any, **object_attributes: Optional[Any]) -> Optional[Any]:
        """
        Method for patching an object.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :param object_attributes: Object attributes.
        :return: Object ID of patched object, if patching was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                getattr(self.model[object_type],
                        self.primary_keys[object_type]) == object_id
            ).first()
            if obj:
                for attribute in object_attributes:
                    setattr(obj, attribute, object_attributes[attribute])
                session.commit()
                result = getattr(obj, self.primary_keys[object_type])
        return result

    def delete_object(self, object_type: str, object_id: Any) -> Optional[Any]:
        """
        Method for deleting an object.
        :param object_type: Target object type.
        :param object_id: Target ID.
        :param object_attributes: Object attributes.
        :return: Object ID of patched object, if deletion was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                getattr(self.model[object_type],
                        self.primary_keys[object_type]) == object_id
            ).first()
            if obj:
                obj.delete()
                session.commit()
                result = getattr(obj, self.primary_keys[object_type])
        return result
