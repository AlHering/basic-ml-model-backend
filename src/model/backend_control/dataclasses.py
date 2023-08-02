# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from uuid import uuid4
from sqlalchemy import Column, String, JSON, ForeignKey, BLOB, Integer, DateTime, func, text
from sqlalchemy.ext.automap import automap_base, classname_for_table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.utility.bronze import sqlalchemy_utility


# Taken from https://stackoverflow.com/questions/17277735/using-uuids-in-sqlite and adjusted
UUID_CREATION = text("""cast( lower(hex( randomblob(4)) || '-' || hex( randomblob(2))
         || '-' || '4' || substr( hex( randomblob(2)), 2) || '-'
         || substr('AB89', 1 + (abs(random()) % 4) , 1)  ||
         substr(hex(randomblob(2)), 2) || '-' || hex(randomblob(6))) as varchar)""")


MODEL = {
    "__tablename__": "model",
    "__table_args__": {"comment": "Model Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False, server_default=UUID_CREATION,
                   comment="UUID of the model."),
    "path": Column(String, nullable=False,
                   comment="Path of the model."),
    "model_type": Column(String, nullable=False,
                         comment="Type of the model."),
    "model_loader": Column(String, nullable=False,
                           comment="Loader for the model."),
    "created": Column(DateTime, server_default=func.now(),
                      comment="Timestamp of creation."),
    "updated": Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                      comment="Timestamp of last update.")
}


INSTANCE = {
    "__tablename__": "instance",
    "__table_args__": {"comment": "Instance Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False, server_default=UUID_CREATION,
                   comment="UUID of the model."),
    "config": Column(JSON, nullable=False,
                     comment="Instance configuration."),
    "created": Column(DateTime, server_default=func.now(),
                      comment="Timestamp of creation."),
    "updated": Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                      comment="Timestamp of last update.")
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
    "finished": Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                       comment="Timestamp of reponse transmission.")

}


def create_or_load_database(database_uri: str) -> dict:
    """
    Function for creating or loading backend database.
    :param database_uri: Database URI.
    """
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
