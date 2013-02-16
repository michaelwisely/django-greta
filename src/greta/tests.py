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
        repo = RepoFactory.create()
        self.assertTrue(os.path.exists(repo.path))
        self.assertEqual(repo.repo.path, repo.path)
        self.assertEqual([], repo.branches)
        self.assertEqual([], repo.tags)
