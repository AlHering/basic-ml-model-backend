# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
import unittest
from src.quality.configuration_tests import test_configuration


suite = unittest.TestLoader().loadTestsFromModule(test_configuration)


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
