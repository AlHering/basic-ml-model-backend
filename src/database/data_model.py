# -*- coding: utf-8 -*-
"""
****************************************************
*             Modular Voice Assistant              *
*            (c) 2024 Alexander Hering             *
****************************************************
"""
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Engine, Column, String, JSON, DateTime, func, Boolean, ForeignKey
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from uuid import uuid4
from src.configuration import configuration as cfg


def populate_data_infrastructure(engine: Engine, schema: str, model: dict) -> None:
    """
    Function for populating data infrastructure.
    :param engine: Database engine.
    :param schema: Schema for tables.
    :param model: Model dictionary for holding data classes.
    """
    schema = str(schema)
    if schema and not schema.endswith("."):
        schema += "."
    base = declarative_base()

    class Log(base):
        """
        Log class, representing an log entry, connected to a backend interaction.
        """
        __tablename__ = f"{schema}log"
        __table_args__ = {
            "comment": "Log table.", "extend_existing": True}

        uuid = Column(UUIDType(binary=False), primary_key=True, unique=True, nullable=False, default=uuid4,
                      comment="UUID of the logging entry.")
        request = Column(JSON, nullable=False,
                         comment="Request, sent to the backend.")
        response = Column(JSON, comment="Response, given by the backend.")
        requested = Column(DateTime, server_default=func.now(),
                           comment="Timestamp of request receive.")
        responded = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                           comment="Timestamp of response transmission.")

    class Collection(base):
        """
        Collection class, representing a machine learning model.
        """
        __tablename__ = f"{schema}collection"
        __table_args__ = {
            "comment": "Collection table.", "extend_existing": True}

        uuid = Column(UUIDType(binary=False), primary_key=True, unique=True, nullable=False, default=uuid4,
                      comment="UUID of the logging entry.")
        name = Column(String,
                      comment="Collection name.")
        path = Column(String,
                      comment="Collection root path.")
        description = Column(String,
                             comment="Collection description.")
        config = Column(JSON,
                        comment="Collection config.")

        models = relationship("Model", back_populates="collection")

        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

    class Model(base):
        """
        Model class, representing a machine learning model.
        """
        __tablename__ = f"{schema}model"
        __table_args__ = {
            "comment": "Model table.", "extend_existing": True}

        uuid = Column(UUIDType(binary=False), primary_key=True, unique=True, nullable=False, default=uuid4,
                      comment="UUID of a model.")
        model_type = Column(String,
                            comment="Target model type.")
        engine = Column(String,
                        comment="Model engine.")
        source = Column(String,
                        comment="Model source.")
        name = Column(String,
                      comment="Model name.")
        url = Column(String, unique=True,
                     comment="Model URL.")
        size = Column(String,
                      comment="Model size.")
        primary_file = Column(String,
                              comment="Model primary file.")
        path = Column(String,
                      comment="Model folder path.")
        files = Column(JSON,
                       comment="Model files.")

        collection_uuid = mapped_column(ForeignKey(f"{schema}collection.uuid"))
        collection = relationship(
            "Collection", back_populates="models")

        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

    for dataclass in [Log, Collection, Model]:
        model[dataclass.__tablename__.replace(schema, "")] = dataclass

    base.metadata.create_all(bind=engine)


def get_default_entries() -> dict:
    """
    Returns default entries.
    :return: Default entries.
    """
    return {}
