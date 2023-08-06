# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
from src.control.backend_controller import BackendController
from src.configuration import configuration as cfg


TESTING_PROCESSES_PATH = f"{cfg.PATHS.TEST_PATH}/processes"


class BackendControllerTest(unittest.TestCase):
    """
    Test case class for testing the backend controller.
    """

    def test_01_llm_preparation(self):
        """
        Method for testing llm preparation.
        """
        pass

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


if __name__ == '__main__':
    unittest.main()
