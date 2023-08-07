# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Any, Optional, List
from src.utility.bronze import sqlalchemy_utility
from sqlalchemy.ext.automap import automap_base
from src.model.model_control.data_model import populate_data_instrastructure
from src.configuration import configuration as cfg


class ModelDatabase(object):
    """
    Class, representing a model database.
    """

    def __init__(self, database_uri: str = None, schema: str = "", verbose: bool = False) -> None:
        """
        Initiation method.
        :param database_uri: Database URI.
            Defaults to None in which case the central MODEL_DB ENV variable is used.
        :param schema: Schema to use.
            Defaults to empty string in which case no schema is used.
        :param verbose: Verbose flag for interaction methods.
            Defaults to False since archiver is already logging.
        """
        self._logger = cfg.LOGGER
        self.verbose = verbose
        self._logger.info("Automapping existing structures")
        self.base = automap_base()
        self.engine = sqlalchemy_utility.get_engine(
            cfg.ENV["MODEL_DB"] if database_uri is None else database_uri)
        self.base.prepare(autoload_with=self.engine, reflect=True)
        self.session_factory = sqlalchemy_utility.get_session_factory(
            self.engine)
        self._logger.info("base created with")
        self._logger.info(f"Classes: {self.base.classes.keys()}")
        self._logger.info(f"Tables: {self.base.metadata.tables.keys()}")

        self.model = {}
        self.schema = schema
        if self.schema and not self.schema.endswith("."):
            self.schema += "."

        self._logger.info(
            f"Generating model tables for website with schema {schema}")
        populate_data_instrastructure(self.base, self.schema, self.model)
        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        if self.verbose:
            self._logger.info(f"Datamodel after addition: {self.model}")
        self._logger.info("Creating new structures")
        self.base.metadata.create_all(bind=self.engine)

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
                session.delete(obj)
                session.commit()
                result = getattr(obj, self.primary_keys[object_type])
        return result
