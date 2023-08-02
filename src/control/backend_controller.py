# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from time import sleep
from uuid import uuid4
from datetime import datetime as dt
from typing import Optional, Any, List
from src.configuration import configuration as cfg
from src.model.backend_control.llm_pool import LLMPool
from src.model.backend_control.dataclasses import create_or_load_database


class BackendController(object):
    """
    Controller class for handling backend interface requests.
    """

    def __init__(self) -> None:
        """
        Initiation method.
        """
        self.working_directory = os.path.join(cfg.PATHS.BACKEND_PATH, "processes"
                                              )
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)
        self.database_uri = cfg.ENV.get(
            "BACKEND_DATABASE", f"sqlite:///{self.working_directory}/backend.db")
        representation = create_or_load_database(self.database_uri)
        self.base = representation["base"]
        self.engine = representation["engine"]
        self.model = representation["model"]
        self.session_factory = representation["session_factory"]
        self.primary_keys = {object_class: self.model[object_class].primary_key.columns.values()[
            0].name for object_class in self.model}

        # TODO: Include priority and interrupt system when implemented in LLMPool class.
        self._cache = {}
        self.llm_pool = LLMPool()

    def shutdown(self) -> None:
        """
        Method for running shutdown process.
        """
        self.llm_pool.stop_all()
        while any(self.llm_pool.is_running(self._cache[instance_uuid]["thread"]) for instance_uuid in self._cache):
            sleep(2.0)

    def load_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for loading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Thread UUID.
        """
        if instance_uuid in self._cache:
            if not self.llm_pool.is_running(self._cache[instance_uuid]["thread"]):
                self.llm_pool.load_llm(self._cache[instance_uuid]["thread"])
                self._cache[instance_uuid]["restarted"] += 1
        else:
            self._cache[instance_uuid] = {
                "thread": None,
                "started": None,
                "restarted": 0,
                "accessed": 0,
                "inactive": 0
            }
            self._cache[instance_uuid]["thread"] = self.llm_pool.prepare_llm(self.get_object(
                "instance", instance_uuid).config)
            self.llm_pool.load_llm(self._cache[instance_uuid])
            self._cache[instance_uuid]["started"] = dt.now()
        return self._cache[instance_uuid]

    def unload_instance(self, instance_uuid: str) -> Optional[str]:
        """
        Method for unloading a configured language model instance.
        :param instance_uuid: Instance UUID.
        :return: Thread UUID.
        """
        if instance_uuid in self._cache:
            if self.llm_pool.is_running(self._cache[instance_uuid]["thread"]):
                self.llm_pool.unload_llm(self._cache[instance_uuid]["thread"])
            return self._cache[instance_uuid]["thread"]
        else:
            return None

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
