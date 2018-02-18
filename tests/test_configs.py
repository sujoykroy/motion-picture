import unittest
import sys
from img2vid.configs import EnvironConfig

class FakeWand:
    @property
    def api(self):
        raise ImportError

class TestConfigs(unittest.TestCase):
    def tearDown(self):
        if "_orig_wand" in sys.modules:
            sys.modules["wand"] = sys.modules["_orig_wand"]
            del sys.modules["_orig_wand"]
        else:
            del sys.modules["wand"]

    def test_magick_home(self):
        wand = FakeWand()
        if "wand" in sys.modules:
            sys.modules["_orig_wand"] = sys.modules["wand"]
        sys.modules["wand"] = wand
        #self.assertFalse(EnvironConfig.is_magick_found())#TODO

if __name__ == "__main__":
    unittest.main()

