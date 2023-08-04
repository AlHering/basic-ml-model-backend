# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
import os
import shutil
from datetime import datetime
from typing import Any
from src.configuration import configuration as cfg
from src.model.backend_control.dataclasses import create_or_load_database, sqlalchemy_utility


TESTING_DB_PATH = f"{cfg.PATHS.TEST_PATH}/backend.db"


class DataclassesTest(unittest.TestCase):
    """
    Test case class for testing URL configuration.
    """

    def test_01_infrastructure(self) -> None:
        """
        Method for testing basic infrastructure.
        """
        self.assertTrue(os.path.exists(TESTING_DB_PATH))
        self.assertTrue(all(key in self.data_infrastructure for key in [
                        "base", "engine", "model", "session_factory"]))
        self.assertEqual(len(
            [c for c in self.data_infrastructure["base"].metadata.tables["model"].columns]), 6)
        self.assertEqual(len(
            [c for c in self.data_infrastructure["base"].metadata.tables["instance"].columns]), 5)
        self.assertEqual(len(
            [c for c in self.data_infrastructure["base"].metadata.tables["log"].columns]), 5)

    def test_02_key_constraints(self) -> None:
        """
        Method for testing key constraints.
        """
        self.assertEqual(
            list(self.data_infrastructure["base"].metadata.tables["model"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.data_infrastructure["base"].metadata.tables["model"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))
        self.assertEqual(list(self.data_infrastructure["base"].metadata.tables["instance"].foreign_keys)[
            0].column.table.name, "model")
        self.assertEqual(list(self.data_infrastructure["base"].metadata.tables["instance"].foreign_keys)[
            0].target_fullname, "model.id")
        self.assertEqual(
            list(self.data_infrastructure["base"].metadata.tables["instance"].primary_key.columns)[0].name, "uuid")

        self.assertTrue(
            isinstance(list(self.data_infrastructure["base"].metadata.tables["instance"].primary_key.columns)[0].type, sqlalchemy_utility.Uuid))
        self.assertEqual(
            list(self.data_infrastructure["base"].metadata.tables["log"].primary_key.columns)[0].name, "id")
        self.assertTrue(
            isinstance(list(self.data_infrastructure["base"].metadata.tables["log"].primary_key.columns)[0].type, sqlalchemy_utility.Integer))

    def test_03_model_key_representation(self) -> None:
        """
        Method for testing model representation.
        """
        primary_keys = {
            object_class: self.data_infrastructure["model"][object_class].__mapper__.primary_key[0].name for object_class in self.data_infrastructure["model"]}
        self.assertEqual(primary_keys["model"], "id")
        self.assertEqual(primary_keys["instance"], "uuid")
        self.assertEqual(primary_keys["log"], "id")

    def test_04_model_object_interaction(self) -> None:
        """
        Method for testing model representation.
        """
        model = self.data_infrastructure["model"]["model"](
            path="my_path",
            type="my_type",
            loader="my_loader"
        )
        self.assertTrue(all(hasattr(model, attribute) for attribute in [
            "id", "path", "type", "loader", "created", "updated"]))

        instance = self.data_infrastructure["model"]["instance"](
            config={"my_key": "my_value"}
        )
        self.assertTrue(all(hasattr(instance, attribute) for attribute in [
            "uuid", "config", "model_id", "created", "updated"]))

        log = self.data_infrastructure["model"]["log"](
            request={"my_request_key": "my_request_value"}
        )
        self.assertTrue(all(hasattr(log, attribute) for attribute in [
            "id", "request", "response", "started", "finished"]))

        model_id = None
        with self.data_infrastructure["session_factory"]() as session:
            session.add(model)
            session.commit()
            model_id = model.id
        self.assertFalse(model_id is None)

        with self.data_infrastructure["session_factory"]() as session:
            resulting_model = session.query(self.data_infrastructure["model"]["model"]).filter(
                getattr(self.data_infrastructure["model"]["model"], "id") == model_id).first()
        self.assertFalse(resulting_model is None)

        self.assertTrue(isinstance(resulting_model.created,
                        datetime))
        with self.data_infrastructure["session_factory"]() as session:
            resulting_model = session.query(self.data_infrastructure["model"]["model"]).filter(
                getattr(self.data_infrastructure["model"]["model"], "id") == model_id).first()
            resulting_model.path = "my_new_path"
            session.commit()
            session.refresh(resulting_model)
        self.assertEqual(resulting_model.path, "my_new_path")

        instance.model_id = model_id
        with self.data_infrastructure["session_factory"]() as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            resulting_model = session.query(self.data_infrastructure["model"]["model"]).filter(
                getattr(self.data_infrastructure["model"]["model"], "id") == model_id).first()
            self.assertEqual(instance.model_id, resulting_model.id)
            self.assertTrue(isinstance(
                instance.model, self.data_infrastructure["model"]["model"]))

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        if not os.path.exists(cfg.PATHS.TEST_PATH):
            os.makedirs(cfg.PATHS.TEST_PATH)
        cls.data_infrastructure = create_or_load_database(
            f"sqlite:///{TESTING_DB_PATH}")

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        del cls.data_infrastructure
        if os.path.exists(cfg.PATHS.TEST_PATH):
            shutil.rmtree(cfg.PATHS.TEST_PATH, ignore_errors=True)

    @classmethod
    def setup_class(cls):
        """
        Alternative class method for setting up test case.
        """
        cls.setUpClass()

    @classmethod
    def teardown_class(cls):
        """
        Alternative class for setting tearing down test case.
        """
        cls.tearDownClass()


if __name__ == '__main__':
    unittest.main()
