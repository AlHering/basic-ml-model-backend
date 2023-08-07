# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
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
            cfg.ENV["WEBSITE_ARCHIVER_DB"] if database_uri is None else database_uri)
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
            f"Generating archiving tables for website with schema {schema}")
        populate_data_instrastructure(self.base, self.schema, self.model)
        self.primary_keys = {
            object_class: self.model[object_class].__mapper__.primary_key[0].name for object_class in self.model}
        if self.verbose:
            self._logger.info(f"self.model after addition: {self.model}")
        self._logger.info("Creating new structures")
        self.base.metadata.create_all(bind=self.engine)
