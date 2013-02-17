from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

from .validators import repo_name_validator
from .utils import Commiterator

from dulwich.repo import Repo as DulwichRepo
from dulwich.errors import NotGitRepository

import os
import subprocess
import difflib
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
        permissions = (
            ('can_view_repository', 'Can view repository'),
        )

    default_branch = models.CharField(max_length=30, default="master")
    name = models.CharField(max_length=100, unique=True,
                                 validators=[repo_name_validator])

    def __init__(self, *args, **kwargs):
        self._dulwich_repo = None
        super(Repository, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('repo_detail', (), {'pk': self.pk,
                                    'ref': self.default_branch})

    @property
    def path(self):
        return os.path.join(settings.GRETA_ROOT_DIR, self.name)

    @property
    def repo(self):
        if self._dulwich_repo is None:
            self._dulwich_repo = DulwichRepo(self.path)
        return self._dulwich_repo

    def full_ref(self, ref):
        if ref in self.branches:
            ref = 'refs/heads/' + ref
        elif ref in self.tags:
            ref = 'refs/tags/' + ref
        return ref

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

    def get_commit(self, ref):
        return self.repo[self.full_ref(ref)]

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

    def get_log(self, ref=None, start=0, stop=-1):
        return Commiterator(self.repo, ref, start, stop)

    def _run_git_command(self, command):
        git = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=self.path)
        stdout, stderr = git.communicate()

        if stderr:
            logger.error("Error running git command: %s", stderr)

        return stdout

    def show(self, ref):
        ref = self.repo[self.full_ref(ref)].id
        command = ['git', 'show', '--format=oneline', ref]
        _, _, diff = self._run_git_command(command).partition('\n')
        return highlight(diff, DiffLexer(), HtmlFormatter())


@receiver(post_save, sender=Repository)
def create_on_disk_repository(sender, instance, created, **kwargs):
    if created:
        if not os.path.exists(instance.path):
            os.mkdir(instance.path)
            logger.info("Created path for repo at %s", instance.path)
            DulwichRepo.init(instance.path)
            logger.info("Initialized repo at %s", instance.path)
        else:
            logger.info("Path exists for repo at %s", instance.path)
            try:
                DulwichRepo(instance.path)
                logger.info("Path at %s is a valid git repo", instance.path)
            except NotGitRepository:
                logger.error("Path at %s is NOT a git repo", instance.path)
