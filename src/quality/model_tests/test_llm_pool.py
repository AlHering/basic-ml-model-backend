# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
from typing import Optional, Any
from src.configuration import configuration as cfg
from src.model.backend_control import llm_pool as test_llm_pool


def test_spawner(config: str) -> Optional[Any]:
    """
    Function for spawning language model test instance based on configuration.
    :param config: Instance configuration.
    :return: Test language model instance.
    """
    class TestLM(object):
        """
        Test language model class.
        """

        def __init__(self, representation: dict) -> None:
            """
            Initiation method.
            :param representation: Test dictionary for translating prompt to generation reponse.
            """
            self.representation = representation

        def generate(self, prompt: str) -> Optional[Any]:
            """
            Generation method.
            :param prompt: User prompt.
            :return: Response, if generation method is available else None.
            """
            return self.representation[prompt]

    return TestLM(config)


class LLMPoolTest(unittest.TestCase):
    """
    Test case class for testing URL configuration.
    """

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        cls.llm_pool = test_llm_pool.LLMPool()

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        del cls.llm_pool

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
