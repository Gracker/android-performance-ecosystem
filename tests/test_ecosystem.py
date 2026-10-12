import copy
import unittest

from scripts import ecosystem


class EcosystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ecosystem.load_catalog()

    def test_catalog_is_valid(self):
        self.assertEqual([], ecosystem.validate_catalog(self.catalog))

    def test_hub_is_separate_from_seven_core_projects(self):
        self.assertEqual("android-performance-ecosystem", self.catalog["hub"]["id"])
        self.assertEqual(7, len(self.catalog["projects"]))
        self.assertNotIn(
            self.catalog["hub"]["id"],
            {project["id"] for project in self.catalog["projects"]},
        )

    def test_each_language_renders_hub_and_seven_projects(self):
        for language in ecosystem.LANGUAGES:
            snippet = ecosystem.render_snippet(self.catalog, language)
            rows = [line for line in snippet.splitlines() if line.startswith("| ")]
            self.assertEqual(10, len(rows))  # header + divider + hub + seven project rows
            self.assertIn("[Android Performance Ecosystem]", rows[2])

    def test_public_targets_include_both_hub_and_perfetto_tools_readmes(self):
        targets = list(ecosystem.public_targets(self.catalog))
        paths_by_repo = {}
        for target in targets:
            paths_by_repo.setdefault(target["repo"], set()).add(target["path"])

        self.assertEqual(
            {"README.md", "README.zh-CN.md"},
            paths_by_repo["android-performance-ecosystem"],
        )
        self.assertEqual(
            {"README.md", "README.zh-CN.md"},
            paths_by_repo["perfetto-tools"],
        )

    def test_private_project_exposes_no_repository_metadata(self):
        catalog = copy.deepcopy(self.catalog)
        project = next(item for item in catalog["projects"] if item["id"] == "android-internal-wiki")
        project.update(public_url=None, default_branch=None, availability="coming_soon", readmes=[])
        self.assertEqual([], ecosystem.validate_catalog(catalog))
        self.assertIsNone(project["public_url"])
        self.assertIsNone(project["default_branch"])
        self.assertEqual([], project["readmes"])
        for language in ecosystem.LANGUAGES:
            snippet = ecosystem.render_snippet(catalog, language)
            self.assertIn("Coming soon", snippet)
            self.assertIn("| Android Internal Wiki |", snippet)
            self.assertNotIn("[Android Internal Wiki](", snippet)

        project["public_url"] = "https://github.com/example/non-public-project"
        self.assertTrue(ecosystem.validate_catalog(catalog))

    def test_public_wiki_targets_use_its_default_branch_and_readme_languages(self):
        targets = [
            target for target in ecosystem.public_targets(self.catalog)
            if target["repo"] == "android-internals-wiki"
        ]
        self.assertEqual(
            {("master", "README.md", "zh-CN"), ("master", "README.en.md", "en")},
            {(target["branch"], target["path"], target["language"]) for target in targets},
        )

    def test_blog_uses_its_named_site_as_the_primary_address(self):
        project = next(
            item for item in self.catalog["projects"] if item["id"] == "android-performance-blog"
        )
        self.assertEqual("AndroidPerformance.com", project["site_label"])
        for language in ecosystem.LANGUAGES:
            row = next(
                line
                for line in ecosystem.render_snippet(self.catalog, language).splitlines()
                if "| Android Performance Blog" in line
                or "| [Android Performance Blog]" in line
            )
            self.assertLess(row.index("[AndroidPerformance.com]"), row.index("[GitHub]"))

    def test_committed_files_match_catalog(self):
        self.assertEqual([], ecosystem.validate_local_files(self.catalog))


if __name__ == "__main__":
    unittest.main()
