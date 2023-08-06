# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
from src.quality.configuration_tests import test_configuration
from src.quality.model_tests import test_data_model

loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTests(loader.loadTestsFromModule(test_configuration))
suite.addTests(loader.loadTestsFromModule(test_data_model))


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=3).run(suite)
