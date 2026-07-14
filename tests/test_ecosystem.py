import unittest

from scripts import ecosystem


class EcosystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ecosystem.load_catalog()

    def test_catalog_is_valid(self):
        self.assertEqual([], ecosystem.validate_catalog(self.catalog))

    def test_each_language_renders_seven_projects(self):
        for language in ecosystem.LANGUAGES:
            snippet = ecosystem.render_snippet(self.catalog, language)
            rows = [line for line in snippet.splitlines() if line.startswith("| ")]
            self.assertEqual(9, len(rows))  # header + divider + seven project rows

    def test_private_project_exposes_no_repository_metadata(self):
        project = next(item for item in self.catalog["projects"] if item["id"] == "android-internal-wiki")
        self.assertIsNone(project["public_url"])
        self.assertIsNone(project["default_branch"])
        self.assertEqual([], project["readmes"])
        for language in ecosystem.LANGUAGES:
            snippet = ecosystem.render_snippet(self.catalog, language)
            self.assertIn("Coming soon", snippet)
            self.assertIn("| Android Internal Wiki |", snippet)
            self.assertNotIn("[Android Internal Wiki](", snippet)

    def test_committed_files_match_catalog(self):
        self.assertEqual([], ecosystem.validate_local_files(self.catalog))


if __name__ == "__main__":
    unittest.main()
