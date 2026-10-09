import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitor import classify


class TestClassify(unittest.TestCase):
    def test_up(self):
        self.assertEqual(classify(200, 150), "UP")

    def test_slow(self):
        self.assertEqual(classify(200, 1500, slow_ms=1000), "SLOW")

    def test_wrong_status_is_down(self):
        self.assertEqual(classify(500, 100), "DOWN")

    def test_custom_expected_status(self):
        self.assertEqual(classify(301, 100, expected=301), "UP")


if __name__ == "__main__":
    unittest.main()
