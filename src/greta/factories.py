from django.contrib.auth.models import User

from .models import Repository

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
