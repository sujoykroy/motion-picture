import unittest
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

def test_all():
    loader = unittest.TestLoader()
    suite = loader.discover(THIS_DIR)
    return suite