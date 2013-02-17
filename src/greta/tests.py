from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from guardian.shortcuts import assign

from .factories import UserFactory, RepoFactory

import os
import shutil


@override_settings(GRETA_ROOT_DIR=settings.GRETA_ROOT_TEST_DIR)
class RepoTest(TestCase):
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
        self.assertEqual(["refs/heads/master"], repo.branches)
        # derp.txt exists in the tree (look at the definition of RepoFactory)
        self.assertEqual(["derp.txt"], repo.get_tree('HEAD').keys())


@override_settings(GRETA_ROOT_DIR=settings.GRETA_ROOT_TEST_DIR)
class RepoViewsTest(TestCase):
    def setUp(self):
        if os.path.exists(settings.GRETA_ROOT_TEST_DIR):
            shutil.rmtree(settings.GRETA_ROOT_TEST_DIR)
        os.mkdir(settings.GRETA_ROOT_DIR)

        self.alice = UserFactory.create()
        self.bob = UserFactory.create()
        self.alice_repo = RepoFactory.create(num_commits=3)
        self.bob_repo = RepoFactory.create(num_commits=5)
        assign('can_view_repository', self.alice, self.alice_repo)
        assign('can_view_repository', self.bob, self.bob_repo)

    def assertAuthorized(self, username, password, url):
        self.client.login(username=username, password=password)
        r = self.client.get(url)
        self.assertEqual(200, r.status_code)
        self.client.logout()

    def assertUnauthorized(self, username, password, url):
        self.client.login(username=username, password=password)
        r = self.client.get(url)
        self.assertEqual(403, r.status_code)
        self.client.logout()

    def test_access_repo_detail(self):
        """Authorized access repo_detail"""
        self.assertAuthorized(self.alice.username, '123',
                              self.alice_repo.get_absolute_url())
        self.assertAuthorized(self.bob.username, '123',
                              self.bob_repo.get_absolute_url())

    def test_unauthorized_access_repo_detail(self):
        """Unauthorized access repo_detail"""
        self.assertUnauthorized(self.bob.username, '123',
                                self.alice_repo.get_absolute_url())
        self.assertUnauthorized(self.alice.username, '123',
                              self.bob_repo.get_absolute_url())
