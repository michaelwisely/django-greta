from django.contrib.auth.models import User
from django.db.models.signals import post_save
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from time import time

from .models import Repository

import os
import factory
import logging

logger = logging.getLogger(__name__)


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: "user-{}".format(n))
    password = "123"

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class RepoFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Repository

    name = factory.Sequence(lambda n: 'repository-{0}.git'.format(n))

    @classmethod
    def create(cls, **kwargs):
        # Since the create_on_disk_repository signal receiver makes a
        # change to the Repository instance, we have to query the
        # database to get the updated object before returning it.
        obj = super(RepoFactory, cls).create(**kwargs)
        return cls.FACTORY_FOR.objects.get(pk=obj.pk)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        # The DjangoModelFactory performs an additional save() at the
        # end, that we don't want. This overrides that method and
        # prevents the save from happening.
        pass

    @factory.post_generation
    def num_commits(self, create, extracted, **kwargs):
        """Creates "num_commits" commits in the Repository's on disk git
        repo. You can specify the number of commits in the on disk
        repo by passing a "num_commits" keyword argumetn to
        RepoFactory.create()

        """
        if not create:
            return

        num_commits = extracted or 0
        if num_commits > 0:
            logger.debug("Adding commits to {}".format(self.name))
            if not create:
                raise Exception("Cannot add commits if repo not created")

            RepoFactory._do_commits(self.repo, num_commits)

        return extracted or 0

    @classmethod
    def _file_contents(cls):
        """Create a random string"""
        return ''.join(chr(ord(x) % 26 + 65) for x in os.urandom(32))

    @classmethod
    def _commit(cls, message, tree, parent_commit):
        """Creates a Commit instance, but doesn't actually add it to the
        repo's object store.

        """
        commit = Commit()
        commit.tree = tree.id
        commit.author = commit.committer = "Shark-o <sharko@derp.com>"
        commit.commit_time = commit.author_time = int(time())
        commit.commit_timezone = commit.author_timezone = parse_timezone('-0200')[0]
        commit.encoding = "UTF-8"
        commit.message = message

        if parent_commit:
            commit.parents = [parent_commit.id]

        return commit

    @classmethod
    def _do_commits(cls, repo, num_commits=1):
        """Add commits to the repo.

        """
        if num_commits > 1:
            # If there are parent commits, we recurse to get the parent
            # commit's repository objects
            parent_commit = cls._do_commits(repo, num_commits - 1)
        else:
            # Otherwise, we're just making the one commit, so we can
            # create the objects by hand.

            # No parent commits
            parent_commit = None

        # Create the file
        blob = Blob.from_string(cls._file_contents())

        # Create the path for it
        tree = Tree()
        tree.add("file.txt", 0100644, blob.id)

        # Create a commit object
        msg = "Commit #{}".format(num_commits)
        commit = cls._commit(msg, tree, parent_commit)

        # Add the commit stuff to the repo's object store
        object_store = repo.object_store
        object_store.add_object(blob)
        object_store.add_object(tree)
        object_store.add_object(commit)

        # Point 'master' to the commit
        repo.refs['refs/heads/master'] = commit.id

        return commit
