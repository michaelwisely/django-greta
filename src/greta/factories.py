from django.contrib.auth.models import User
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
    def _file_contents(cls):
        """Create a random string"""
        return ''.join(chr(ord(x) % 26 + 65) for x in os.urandom(32))

    @classmethod
    def _commit(cls, message, tree, parent_commits):
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

        if parent_commits:
            commit.parents = parent_commits

        return commit

    @classmethod
    def _do_commits(cls, repo, num_commits=0):
        """Add commits to the repo.

        """
        if num_commits > 0:
            # If there are parent commits, we recurse to get the parent
            # commit's repository objects
            blob, tree, parent_commit = cls._do_commits(repo, num_commits - 1)

            # Update the contents of the file and tree
            blob.data = cls._file_contents()
            tree["file.txt"] = (0100644, blob.id)
        else:
            # Otherwise, we're just making the one commit, so we can
            # create the objects by hand.

            # No parent commits
            parent_commit = []

            # Create the file
            blob = Blob.from_string(cls._file_contents())

            # Create the path for it
            tree = Tree()
            tree.add("file.txt", 0100644, blob.id)

        # Create a commit object
        msg = "Commit #{}".format(num_commits)
        commit = cls._commit(msg, tree, [parent_commit])

        # Add the commit stuff to the repo's object store
        object_store = repo.object_store
        object_store.add_object(blob)
        object_store.add_object(tree)
        object_store.add_object(commit)

        # Point 'master' to the commit
        repo.refs['refs/heads/master'] = commit.id

        return (blob, tree, commit)

    @classmethod
    def _prepare(cls, create, **kwargs):
        num_commits = kwargs.pop('num_commits', 0)
        repo = super(RepoFactory, cls)._prepare(create, **kwargs)
        if num_commits > 0:
            logger.debug("Adding commits to {}".format(repo.name))
            if not create:
                raise Exception("Cannot add commits if repo not created")
            repo.save()
            RepoFactory._do_commits(repo.repo, num_commits)
        return repo
