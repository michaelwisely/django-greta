from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver

from .validators import repo_name_validator

from dulwich.repo import Repo as DulwichRepo

import os
import logging

logger = logging.getLogger(__name__)


def path_to_list(path):
    head, tail = os.path.split(path)
    if head in ('', '/') and tail == '':
        return ()
    return path_to_list(head) + (tail,)


class Repository(models.Model):
    class Meta:
        verbose_name_plural = 'Repositories'
    repo_name = models.CharField(max_length=100, unique=True,
                                 validators=[repo_name_validator])

    def __init__(self, *args, **kwargs):
        self._dulwich_repo = None
        super(Repository, self).__init__(*args, **kwargs)

    @property
    def path(self):
        return os.path.join(settings.GRETA_ROOT_DIR, self.repo_name)

    @property
    def repo(self):
        if self._dulwich_repo is None:
            self._dulwich_repo = DulwichRepo(self.path)
        return self._dulwich_repo

    def _filter_branch(self, ref_prefix=''):
        len_prefix = len(ref_prefix)
        refs = self.repo.get_refs().keys()
        return [r[len_prefix:] for r in refs if r.startswith(ref_prefix)]

    @property
    def branches(self):
        return self._filter_branch('refs/heads/')

    @property
    def tags(self):
        return self._filter_branch('refs/tags/')

    def _subtree(self, tree, tree_path=''):
        tree_dict = dict((path, self.repo[sha])
                         for _, path, sha in tree.entries())
        if tree_path:
            path_list = tree_path.split('/')
            top_dir, tree_path = path_list[0], '/'.join(path_list[1:])
            return self._subtree(tree_dict[top_dir], tree_path)
        return tree_dict

    def get_tree(self, ref, tree_path=''):
        return self._subtree(self.repo[self.repo[ref].tree], tree_path)


@receiver(post_save, sender=Repository)
def create_on_disk_repository(sender, instance, created, **kwargs):
    if created:
        if not os.path.exists(instance.path):
            os.mkdir(instance.path)
            logger.info("Created path for repo at %s", instance.path)
        DulwichRepo.init(instance.path)
        logger.info("Initialized repo at %s", instance.path)
