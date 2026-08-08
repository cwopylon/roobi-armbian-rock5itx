import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate import parse_content_length, should_skip_existing_manifest


class GenerateTests(unittest.TestCase):
    def test_parse_content_length(self) -> None:
        self.assertEqual(parse_content_length("12345"), 12345)
        self.assertIsNone(parse_content_length(None))
        self.assertIsNone(parse_content_length("not-a-number"))

    def test_should_skip_existing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "image.json"
            payload = {
                "name": "Example",
                "version": "1.0",
                "download": [{"size": 123}],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertTrue(should_skip_existing_manifest(path, "Example", "1.0"))
            self.assertFalse(should_skip_existing_manifest(path, "Example", "2.0"))

            payload["download"][0]["size"] = 0
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(should_skip_existing_manifest(path, "Example", "1.0"))


if __name__ == "__main__":
    unittest.main()
