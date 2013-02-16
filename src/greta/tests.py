from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from .factories import UserFactory, RepoFactory

import os
import shutil


@override_settings(GRETA_ROOT_DIR=settings.GRETA_ROOT_TEST_DIR)
class SimpleTest(TestCase):
    def setUp(self):
        if os.path.exists(settings.GRETA_ROOT_TEST_DIR):
            shutil.rmtree(settings.GRETA_ROOT_TEST_DIR)
        os.mkdir(settings.GRETA_ROOT_DIR)

    def test_create_repo(self):
        """Create a repo"""
        repo = RepoFactory.create()
        # Check paths
        self.assertTrue(os.path.exists(repo.path))
        self.assertEqual(repo.repo.path, repo.path)
        # No branches or tags yet. It's blank
        self.assertEqual([], repo.branches)
        self.assertEqual([], repo.tags)

    def test_list_branches(self):
        """List branches"""
        # Create a repo with a history of two commits
        repo = RepoFactory.create(num_commits=2)
        # Master was created
        self.assertEqual(["master"], repo.branches)
        # derp.txt exists in the tree (look at the definition of RepoFactory)
        self.assertEqual(["derp.txt"], repo.get_tree('HEAD').keys())
