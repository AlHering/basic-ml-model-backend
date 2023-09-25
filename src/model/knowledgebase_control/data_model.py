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
        filename = Column(Text, nullable=True,
                         comment="Document filename.")
        extension = Column(String, nullable=True,
                         comment="Document file extension.")
        part = Column(Integer, nullable=False, default=-1.
                         comment="Document part number.")
        content = Column(Text, nullable=False,
                         comment="Document content.")
        meta_data = Column(JSON, comment="Document metadata.")
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

    for dataclass in [Knowledgebase, Document]:
        model[dataclass.__tablename__.replace(schema, "")] = dataclass

    base.metadata.create_all(bind=engine)
