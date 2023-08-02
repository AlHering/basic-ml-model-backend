# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import os
from uuid import uuid4
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

    def shutdown(self) -> None:
        """
        Method for running shutdown process.
        """
        pass

    def get_objects(self, object_type: str) -> List[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :return: List of objects of given type.
        """
        return self.session_factory().query(self.model[object_type]).all()

    def get_object(self, object_type: str, object_uuid: str) -> Optional[Any]:
        """
        Method for acquiring objects.
        :param object_type: Target object type.
        :param object_uuid: Target UUID.
        :return: An object of given type and UUID, if found.
        """
        return self.session_factory().query(self.model[object_type]).filter(
            self.model[object_type].uuid == object_uuid
        ).first()

    def post_object(self, object_type: str, **object_attributes: Optional[Any]) -> Optional[str]:
        """
        Method for adding an object.
        :param object_type: Target object type.
        :param object_attributes: Object attributes.
        :return: Object UUID of added object, if adding was successful.
        """
        if "uuid" not in object_attributes:
            object_attributes["uuid"] = str(uuid4())
        obj = self.model[object_type](**object_attributes)
        with self.session_factory() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj.uuid

    def patch_object(self, object_type: str, object_uuid: str, **object_attributes: Optional[Any]) -> Optional[str]:
        """
        Method for patching an object.
        :param object_type: Target object type.
        :param object_uuid: Target UUID.
        :param object_attributes: Object attributes.
        :return: Object UUID of patched object, if patching was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                self.model[object_type].uuid == object_uuid
            ).first()
            if obj:
                for attribute in object_attributes:
                    setattr(obj, attribute, object_attributes[attribute])
                session.commit()
                result = obj.uuid
        return result

    def delete_object(self, object_type: str, object_uuid: str) -> Optional[str]:
        """
        Method for deleting an object.
        :param object_type: Target object type.
        :param object_uuid: Target UUID.
        :param object_attributes: Object attributes.
        :return: Object UUID of patched object, if deletion was successful.
        """
        result = None
        with self.session_factory() as session:
            obj = session.query(self.model[object_type]).filter(
                self.model[object_type].uuid == object_uuid
            ).first()
            if obj:
                obj.delete()
                session.commit()
                result = obj.uuid
        return result
