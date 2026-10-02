import unittest

from validate_branch_flow import BOOTSTRAP_BRANCH, validate


class BranchFlowTests(unittest.TestCase):
    def test_develop_accepts_work_and_release_sync(self):
        for head in ("codex/work", "codex/restore-release-operation", "deploy/2026-10-03.1"):
            validate("develop", head, ["deploys/app/compose.yml"])

    def test_main_accepts_versioned_release(self):
        validate("main", "deploy/2026-10-03.1", ["deploys/app/compose.yml"])

    def test_main_rejects_ordinary_and_invalid_release_branches(self):
        for head in ("codex/work", "develop", "deploy/test", "deploy/2026-10-03.0"):
            with self.subTest(head=head), self.assertRaisesRegex(ValueError, "target develop"):
                validate("main", head, ["deploys/app/compose.yml"])

    def test_bootstrap_only_accepts_release_tooling(self):
        validate("main", BOOTSTRAP_BRANCH, [
            ".github/workflows/prepare-release.yml", "scripts/patchnotes/common.py",
            "docs/patch-notes.md", "AGENTS.md", "changes/released/.gitkeep",
        ])
        for path in ("deploys/app/compose.yml", "minecraft/java/plugins/CraftBook/config.yml",
                     "changes/pending/new-feature.md", ".github/workflows/deploy.yml"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "only change release tooling"):
                validate("main", BOOTSTRAP_BRANCH, [path])


if __name__ == "__main__":
    unittest.main()
