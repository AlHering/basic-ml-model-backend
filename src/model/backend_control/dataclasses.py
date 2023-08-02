# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy import Column, String, JSON, ForeignKey, BLOB
from sqlalchemy.ext.automap import automap_base, classname_for_table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.utility.bronze import sqlalchemy_utility


CONTROLLER = {
    "__tablename__": "controller",
    "__table_args__": {"comment": "Controller Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the controller."),
    "language_model_uuid": Column(String, ForeignKey(f"model.uuid"),
                                  comment="Registered language model to use."),

    "knowledgebase_uuid": Column(String, ForeignKey(f"knowledgebase.uuid"),
                                 comment="Registered knowledgebase to use.")
}


MODEL = {
    "__tablename__": "model",
    "__table_args__": {"comment": "Model Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the model."),
    "path": Column(String, nullable=False,
                   comment="Path of the model."),
    "model_type": Column(String, nullable=False,
                         comment="Type of the model."),
    "model_loader": Column(String, nullable=False,
                           comment="Loader for the model.")
}


KNOWLEDGEBASE = {
    "__tablename__": "knowledgebase",
    "__table_args__": {"comment": "Knowledgebase Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the knowledgebase."),
    "path": Column(String, nullable=False,
                   comment="Path to the knowledgebase."),
    "loader": Column(String, nullable=False,
                     comment="Loader for knowledgebase."),
    "embedding_model_uuid": Column(String, ForeignKey(f"model.uuid"),
                                   comment="Registered embedding model to use."),
    "documents": relationship("Document")

}


DOCUMENT = {
    "__tablename__": "document",
    "__table_args__": {"comment": "Document Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the document."),
    "content": Column(BLOB, comment="Content of the document."),
    "meta_data": Column(JSON, comment="Metadata of the document.")
}


CONVERSATION = {
    "__tablename__": "conversation",
    "__table_args__": {"comment": "Conversation Table."},
    "uuid": Column(String, primary_key=True, unique=True, nullable=False,
                   comment="UUID of the conversation."),
    "controller_uuid": Column(String, ForeignKey(f"model.uuid"),
                              comment="UUID of managing controller."),
    "conversation_content": Column(JSON, comment="Conversation content.")

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

        for dataclass_content in [CONTROLLER, MODEL, KNOWLEDGEBASE, DOCUMENT, CONVERSATION]:
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
