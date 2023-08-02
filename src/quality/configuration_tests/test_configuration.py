# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
import re
from src.configuration import configuration as cfg


class ConfigurationTest(unittest.TestCase):
    """
    Test case class for testing URL configuration.
    """

    def test_urls(self):
        for attribute in dir(cfg.URLS)

    @classmethod
    def setUpClass(cls):
        """
        Class method for setting up test case.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Class method for setting tearing down test case.
        """
        pass

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
