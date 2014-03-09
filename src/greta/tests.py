from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from guardian.shortcuts import assign_perm

from .factories import UserFactory, RepoFactory

import os
import shutil


@override_settings(GRETA_ROOT_DIR=settings.GRETA_ROOT_TEST_DIR)
@override_settings(CELERY_ALWAYS_EAGER=True)
class RepoBasicTest(TestCase):
    def setUp(self):
        if os.path.exists(settings.GRETA_ROOT_TEST_DIR):
            shutil.rmtree(settings.GRETA_ROOT_TEST_DIR)
        os.mkdir(settings.GRETA_ROOT_DIR)

    def test_create_repo(self):
        """Create a repo"""
        repo = RepoFactory.create()

        # Check paths
        self.assertTrue(os.path.exists(repo.path),
                        msg=repo.path + " does not exist")
        self.assertEqual(repo.repo.path, repo.path)
        # No branches or tags yet. It's blank
        self.assertEqual([], repo.branches)
        self.assertEqual([], repo.tags)

    def test_repo_factory(self):
        """Create a repo with commits"""
        repo = RepoFactory.create(num_commits=6)

        # Check paths
        self.assertTrue(os.path.exists(repo.path),
                        msg=repo.path + " does not exist")
        self.assertEqual(repo.repo.path, repo.path)

        # Assert we have master, but no tags
        self.assertEqual(['refs/heads/master'], repo.branches)
        self.assertEqual([], repo.tags)

        revisions = list(repo.repo.get_walker())
        self.assertEqual(6, len(revisions))

    def test_fork_repo(self):
        """Fork a repo"""
        base = RepoFactory.create(num_commits=5)
        fork = RepoFactory.create(forked_from=base)

        # Check paths
        self.assertTrue(os.path.exists(base.path),
                        msg=base.path + " does not exist")
        self.assertTrue(os.path.exists(fork.path),
                        msg=fork.path + " does not exist")
        self.assertEqual(fork.repo.path, fork.path)

        # Same head as parent
        self.assertEqual(base.repo.head(), fork.repo.head())

    def test_list_branches(self):
        """List branches"""
        # Create a repo with a history of two commits
        repo = RepoFactory.create(num_commits=2)
        # Master was created
        self.assertEqual(["refs/heads/master"], repo.branches)
        # file.txt exists in the tree (look at the definition of RepoFactory)
        self.assertEqual(["file.txt"], repo.get_tree('HEAD').keys())


@override_settings(GRETA_ROOT_DIR=settings.GRETA_ROOT_TEST_DIR)
@override_settings(CELERY_ALWAYS_EAGER=True)
class RepoViewsTest(TestCase):
    def setUp(self):
        if os.path.exists(settings.GRETA_ROOT_TEST_DIR):
            shutil.rmtree(settings.GRETA_ROOT_TEST_DIR)
        os.mkdir(settings.GRETA_ROOT_DIR)

        self.alice = UserFactory.create()
        self.bob = UserFactory.create()
        self.alice_repo = RepoFactory.create(num_commits=3)
        self.bob_repo = RepoFactory.create(num_commits=5)
        assign_perm('can_view_repository', self.alice, self.alice_repo)
        assign_perm('can_view_repository', self.bob, self.bob_repo)

    def assertAuthorized(self, username, password, url):
        """User can view a repo if they have permissions"""
        self.client.login(username=username, password=password)
        r = self.client.get(url)
        self.assertEqual(200, r.status_code)
        self.client.logout()

    def assertUnauthorized(self, username, password, url):
        """User CANNOT view a repo if they do NOT have permissions"""
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
