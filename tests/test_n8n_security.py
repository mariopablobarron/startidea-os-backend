from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from n8n_config import ConfigError, load_n8n_config


class N8nSecurityTests(unittest.TestCase):
    def _environment(self, directory: str) -> dict[str, str]:
        return {
            "N8N_API_URL": "https://automation.example.test/api/v1",
            "N8N_API_KEY": "test-only-key-at-least-twenty-characters",
            "N8N_TELEGRAM_CREDENTIAL_ID": "credential-id",
            "N8N_WORKFLOW_DIR": directory,
        }

    def test_missing_key_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = self._environment(directory)
            del environment["N8N_API_KEY"]
            with self.assertRaisesRegex(ConfigError, "N8N_API_KEY"):
                load_n8n_config(environment)

    def test_cleartext_and_url_credentials_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for url in (
                "http://automation.example.test/api/v1",
                "https://user:pass@automation.example.test/api/v1",
                "https://automation.example.test/api/v1?key=value",
                "https://automation.example.test/other",
            ):
                environment = self._environment(directory)
                environment["N8N_API_URL"] = url
                with self.assertRaises(ConfigError, msg=url):
                    load_n8n_config(environment)

    def test_valid_configuration_does_not_expose_key_in_repr(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = self._environment(directory)
            config = load_n8n_config(environment)
            self.assertEqual(config.api_url, environment["N8N_API_URL"])
            self.assertNotIn(environment["N8N_API_KEY"], repr(config))

    def test_current_tree_contains_no_published_n8n_key_prefix(self) -> None:
        root = Path(__file__).resolve().parents[1]
        leaked_prefix = "n8n" + "_api_"
        text_suffixes = {
            ".css",
            ".html",
            ".js",
            ".json",
            ".md",
            ".py",
            ".sql",
            ".txt",
            ".yaml",
            ".yml",
        }
        matches: list[str] = []
        for path in root.rglob("*"):
            if ".git" in path.parts or path.suffix not in text_suffixes or not path.is_file():
                continue
            if leaked_prefix in path.read_text(encoding="utf-8", errors="ignore"):
                matches.append(str(path.relative_to(root)))
        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
