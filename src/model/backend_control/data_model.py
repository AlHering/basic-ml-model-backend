# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy.orm import relationship, mapped_column, declarative_base
from sqlalchemy import Engine, Column, String, JSON, ForeignKey, Integer, DateTime, func, Uuid, Text, event, Boolean
from uuid import uuid4, UUID
from typing import Any


def populate_data_instrastructure(engine: Engine, schema: str, model: dict) -> None:
    """
    Function for populating data infrastructure.
    :param engine: Database engine.
    :param schema: Schema for tables.
    :param model: Model dictionary for holding data classes.
    """
    schema = str(schema)
    if not schema.endswith("."):
        schema += "."
    base = declarative_base()

    class Knowledgebase(base):
        """
        Knowledgebase class, representing an knowledge base config..
        """
        __tablename__ = f"{schema}knowledgebase"
        __table_args__ = {
            "comment": "Knowledgebase table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the knowledgebase.")
        persistant_directory = Column(String, nullable=False,
                                      comment="Knowledgebase persistant directory.")
        document_directory = Column(String, nullable=False,
                                    comment="Knowledgebase document directory.")
        handler = Column(String, nullable=False, default="chromadb",
                         comment="Knowledgebase handler.")
        implementation = Column(String, nullable=False, default="duckdb+parquet",
                                comment="Handler implementation.")

        meta_data = Column(JSON, comment="Knowledgebase metadata.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

        documents = relationship(
            "Document", back_populates="knowledgebase")
        embedding_instance_id = mapped_column(
            Integer, ForeignKey(f"{schema}modelinstance.id"))
        embedding_instance = relationship("Modelinstance")

    class Document(base):
        """
        Document class, representing an document.
        """
        __tablename__ = f"{schema}document"
        __table_args__ = {
            "comment": "Document table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the document.")
        content = Column(JSON, nullable=False,
                         comment="Document content.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

        knowledgebase_id = mapped_column(
            Integer, ForeignKey(f"{schema}knowledgebase.id"))
        knowledgebase = relationship(
            "Knowledgebase", back_populates="documents")

    class Modelinstance(base):
        """
        Modelinstance class, representing a machine learning model (version) instance.
        """
        __tablename__ = f"{schema}modelinstance"
        __table_args__ = {
            "comment": "Model instance table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the modelinstance.")
        backend = Column(String, nullable=False,
                         comment="Backend of the model instance.")
        loader = Column(String,
                        comment="Loader for the model instance.")
        loader_kwargs = Column(JSON,
                               comment="Additional loading keyword arguments.")
        gateway = Column(String,
                         comment="Gateway for instance interaction.")
        meta_data = Column(JSON,
                           comment="Metadata of the model instance.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

    class Log(base):
        """
        Log class, representing an log entry, connected to a machine learning model or model version interaction.
        """
        __tablename__ = f"{schema}log"
        __table_args__ = {
            "comment": "Log table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False,
                    comment="ID of the logging entry.")
        request = Column(JSON, nullable=False,
                         comment="Request, sent to the backend.")
        response = Column(JSON, comment="Response, given by the backend.")
        requested = Column(DateTime, server_default=func.now(),
                           comment="Timestamp of request recieval.")
        responded = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                           comment="Timestamp of reponse transmission.")

    for dataclass in [Knowledgebase, Document, Modelinstance, Log]:
        model[dataclass.__tablename__.replace(schema, "")] = dataclass

    base.metadata.create_all(bind=engine)
