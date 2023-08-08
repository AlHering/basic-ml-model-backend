# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Engine, Column, String, JSON, ForeignKey, Integer, DateTime, func, Uuid, Text, event, Boolean
from uuid import uuid4
from typing import Any


def populate_data_instrastructure(base: Any, engine: Engine, schema: str, model: dict) -> None:
    """
    Function for populating data infrastructure.
    :param base: Mapper base.
    :param engine: Database engine.
    :param schema: Schema for tables.
    :param model: Model dictionary for holding data classes.
    """
    schema = str(schema)

    class Model(base):
        """
        Model class, representing a machine learning model.
        """
        __tablename__ = f"{schema}model"
        __table_args__ = {
            "comment": "Model table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the model.")
        path = Column(String,
                      comment="Path of the model folder.")
        task = Column(String,
                      comment="Task of the model.")
        architecture = Column(String,
                              comment="Architecture/basemodel of the model.")
        url = Column(String,
                     comment="URL for the model.")
        meta_data = Column(JSON,
                           comment="Metadata of the model.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

        modelversions = relationship(
            "Modelversion", back_populates="model", viewonly=True)
        instances = relationship(
            "Modelinstance", back_populates="model", viewonly=True)
        assets = relationship("Asset", back_populates="model", viewonly=True)

    class Modelversion(base):
        """
        Modelversion class, representing a machine learning model version.
        """
        __tablename__ = f"{schema}modelversion"
        __table_args__ = {
            "comment": "Model version table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the modelversion.")
        path = Column(String, nullable=False,
                      comment="Relative path of the modelversion.")
        format = Column(String, nullable=False,
                        comment="Format of the modelversion.")
        url = Column(String,
                     comment="URL for the modelversion.")
        sha256 = Column(Text,
                        comment="SHA256 hash for the modelversion.")
        meta_data = Column(JSON,
                           comment="Metadata of the modelversion.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

        model_id = mapped_column(Integer, ForeignKey(f"{schema}model.id"))
        model = relationship(
            "Model", back_populates="modelversions")
        instances = relationship(
            "Modelinstance", back_populates="modelversion", viewonly=True)
        assets = relationship(
            "Asset", back_populates="modelversion", viewonly=True)

    class Modelinstance(base):
        """
        Modelinstance class, representing a machine learning model (version) instance.
        """
        __tablename__ = f"{schema}modelinstance"
        __table_args__ = {
            "comment": "Model instance table.", "extend_existing": True}

        uuid = Column(Uuid, primary_key=True, unique=True, nullable=False, default=uuid4,
                      comment="UUID of the model instance.")
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

        model_id = mapped_column(Integer, ForeignKey(f"{schema}model.id"))
        model = relationship(
            "Model", back_populates="instances")
        modelversion_id = mapped_column(
            Integer, ForeignKey(f"{schema}modelversion.id"))
        modelversion = relationship(
            "Modelversion", back_populates="instances")

    class Asset(base):
        """
        Asset class, representing an asset, connected to a machine learning model or model version.
        """
        __tablename__ = f"{schema}asset"
        __table_args__ = {
            "comment": "Asset table.", "extend_existing": True}

        id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True,
                    comment="ID of the asset.")
        path = Column(String, nullable=False,
                      comment="Path of the asset.")
        type = Column(String, nullable=False,
                      comment="Type of the asset.")
        url = Column(String,
                     comment="URL for the asset.")
        sha256 = Column(Text,
                        comment="SHA256 hash for the asset.")
        meta_data = Column(JSON,
                           comment="Metadata of the asset.")
        created = Column(DateTime, server_default=func.now(),
                         comment="Timestamp of creation.")
        updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now(),
                         comment="Timestamp of last update.")
        inactive = Column(Boolean, nullable=False, default=False,
                          comment="Inactivity flag.")

        model_id = mapped_column(Integer, ForeignKey(f"{schema}model.id"))
        model = relationship(
            "Model", back_populates="assets")
        modelversion_id = mapped_column(
            Integer, ForeignKey(f"{schema}modelversion.id"))
        modelversion = relationship(
            "Modelversion", back_populates="assets")

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

    for dataclass in [Model, Modelversion, Modelinstance, Asset, Log]:
        model[dataclass.__tablename__.replace(schema, "")] = dataclass

    base.metadata.create_all(bind=engine)
    base.prepare(autoload_with=engine)

    @event.listens_for(Modelinstance, "before_insert")
    def generate_uuid(mapper: Any, connect: Any, target: Any) -> None:
        """
        Generation method for UUID, triggered before entry inserts.
        """
        target.uuid = uuid4()
