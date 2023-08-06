# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from uuid import uuid4
from sqlalchemy import Column, String, JSON, ForeignKey, Integer, DateTime, func, Uuid
from sqlalchemy.ext.automap import automap_base, classname_for_table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, mapped_column
from src.utility.bronze import sqlalchemy_utility


MODEL = {
    "__tablename__": "model",
    "__table_args__": {"comment": "Model Table."},
    "id": Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                 comment="UUID of the model."),
    "path": Column(String, nullable=False,
                   comment="Path of the model."),
    "type": Column(String, nullable=False,
                   comment="Type of the model."),
    "loader": Column(String, nullable=False,
                     comment="Loader for the model."),
    "created": Column(DateTime, server_default=func.now(),
                      comment="Timestamp of creation."),
    "updated": Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                      comment="Timestamp of last update."),
    "instances": relationship("Instance", back_populates="model")
}

INSTANCE = {
    "__tablename__": "instance",
    "__table_args__": {"comment": "Instance Table."},
    "uuid": Column(Uuid(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid4,
                   comment="UUID of the instance."),
    "config": Column(JSON, nullable=False,
                     comment="Instance configuration."),
    "created": Column(DateTime, server_default=func.now(),
                      comment="Timestamp of creation."),
    "updated": Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                      comment="Timestamp of last update."),
    "model_id": mapped_column(ForeignKey("model.id")),
    "model": relationship("Model", back_populates="instances")
}

LOG = {
    "__tablename__": "log",
    "__table_args__": {"comment": "Logging Table."},
    "id": Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                 comment="ID of the logging entry."),
    "request": Column(JSON, nullable=False,
                      comment="Request, sent to the backend."),
    "response": Column(JSON, comment="Response, given by the backend."),
    "started": Column(DateTime, server_default=func.now(),
                      comment="Timestamp of request recieval."),
    "finished": Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                       comment="Timestamp of reponse transmission.")
}


def create_or_load_database(database_uri: str, dialect: str = "sqlite") -> dict:
    """
    Function for creating or loading backend database.
    :param database_uri: Database URI.
    :param dialect: Database dialect.
        Defaults to "sqlite".
    """
    if dialect in sqlalchemy_utility.SUPPORTED_DIALECTS:
        base = automap_base()
        engine = sqlalchemy_utility.get_engine(database_uri)
        base.prepare(autoload_with=engine, reflect=True)
        model = {
            table: base.classes[classname_for_table(base, table, base.metadata.tables[table])] for table in
            base.metadata.tables
        }
        session_factory = sqlalchemy_utility.get_session_factory(engine)

        if not model:
            base = declarative_base()

            for dataclass_content in [MODEL, INSTANCE, LOG]:
                if dataclass_content["__tablename__"] not in model:
                    model[dataclass_content["__tablename__"]] = type(
                        dataclass_content["__tablename__"].title(), (base,), dataclass_content)
            base.metadata.create_all(bind=engine)

        return {
            "base": base,
            "engine": engine,
            "model": model,
            "session_factory": session_factory
        }
    else:
        return {}
