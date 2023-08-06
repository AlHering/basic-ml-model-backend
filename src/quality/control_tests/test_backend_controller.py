# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
import gc
import os
import shutil
from src.control.backend_controller import BackendController
from src.model.backend_control.llm_pool import LLMPool
from src.configuration import configuration as cfg


TESTING_PROCESSES_PATH = f"{cfg.PATHS.TEST_PATH}/processes"


class BackendControllerTest(unittest.TestCase):
    """
    Test case class for testing the backend controller.
    """

    def test_01_initiation_process(self):
        """
        Method for testing llm preparation.
        """
        self.assertTrue(os.path.exists(TESTING_PROCESSES_PATH))
        self.assertTrue(all(key in self.data_infrastructure for key in [
                        "base", "engine", "model", "session_factory", "primary_keys", "_cache", "llm_pool"]))
        self.assertTrue(isinstance(self.controller.llm_pool, LLMPool))

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        cls.controller = BackendController(
            working_directory=TESTING_PROCESSES_PATH)

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        del cls.controller

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
        gc.collect()


if __name__ == '__main__':
    unittest.main()
