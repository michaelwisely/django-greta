from django.contrib.auth.models import User

from .models import Repository

import os
import factory


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user' + n)
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


class RepoFactory(factory.Factory):
    FACTORY_FOR = Repository

    repo_name = factory.Sequence(lambda n: 'repository-{0}.git'.format(n))

    @classmethod
    def _prepare(cls, create, **kwargs):
        num_commits = kwargs.pop('num_commits', 0)
        repo = super(RepoFactory, cls)._prepare(create, **kwargs)
        if num_commits > 0:
            if not create:
                raise Exception("Cannot add commits if repo not created")
            repo.save()
            for i in xrange(num_commits):
                with open(os.path.join(repo.path, "derp.txt"), 'a') as derp:
                    derp.write("{0}\n".format(i))
                repo.repo.stage(["derp.txt"])
                repo.repo.do_commit("Commit #{0}".format(i),
                                    committer="Shark-o <sharko@derp.com>")
        return repo
