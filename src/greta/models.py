from django.db import models
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from .validators import repo_name_validator
from .utils import Commiterator, split_diff
from .tasks import setup_repo, archive_old_repository

from celery.result import AsyncResult
from dulwich.repo import Repo as DulwichRepo
from collections import OrderedDict

import os
import subprocess
import logging

logger = logging.getLogger(__name__)


class Repository(models.Model):
    class Meta:
        verbose_name_plural = 'Repositories'
        permissions = (
            ('can_view_repository', 'Can view repository'),
        )

    default_branch = models.CharField(max_length=30, default="master")
    name = models.CharField(max_length=100, unique=True,
                                 validators=[repo_name_validator])
    description = models.TextField()
    forked_from = models.ForeignKey("self", blank=True, null=True,
                                    related_name="forks",
                                    on_delete=models.SET_NULL)
    task_id = models.CharField(max_length=60, null=True, editable=False)

    # Generic Foreign  key to an owning object
    owner_type = models.ForeignKey(ContentType, blank=True, null=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = generic.GenericForeignKey('owner_type', 'owner_id')

    def __init__(self, *args, **kwargs):
        self._dulwich_repo = None
        super(Repository, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        kwargs = {'pk': self.pk,
                  'ref': 'refs/heads/' + self.default_branch}
        return ('repo_detail', (), kwargs)

    @property
    def path(self):
        return os.path.join(settings.GRETA_ROOT_DIR, self.name)

    @property
    def repo(self):
        if self._dulwich_repo is None:
            self._dulwich_repo = DulwichRepo(self.path)
        return self._dulwich_repo

    def _filter_branch(self, ref_prefix=''):
        refs = self.repo.get_refs().keys()
        return [r for r in refs if r.startswith(ref_prefix)]

    @property
    def branches(self):
        return self._filter_branch('refs/heads/')

    @property
    def tags(self):
        return self._filter_branch('refs/tags/')

    def is_ready(self):
        if self.task_id is None:
            return True
        if AsyncResult(self.task_id).ready():
            self.task_id = None
            self.save()
            return True
        return False

    def get_commit(self, ref):
        return self.repo[ref]

    def _subtree(self, tree, tree_path=''):
        tree_dict = OrderedDict(
            (path, sha) for _, path, sha in tree.entries()
        )
        if tree_path:
            top_dir, _, tree_path = tree_path.partition(os.path.sep)
            subtree = self._subtree(self.repo[tree_dict[top_dir]], tree_path)
            tree_dict = OrderedDict((os.path.join(top_dir, path), obj)
                                    for path, obj in subtree.iteritems())
        else:
            tree_dict = OrderedDict((path, self.repo[sha])
                                    for path, sha in tree_dict.iteritems())
        return tree_dict

    def get_tree(self, ref, tree_path=''):
        return self._subtree(self.repo[self.repo[ref].tree], tree_path)

    def get_blob(self, ref, blob_path):
        tree_path = os.path.dirname(blob_path)
        tree = self.get_tree(ref, tree_path)
        return tree[blob_path]

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
        ref = self.repo[ref].id
        command = ['git', 'show', '--format=oneline', ref]
        _, _, diff = self._run_git_command(command).partition('\n')
        return split_diff(diff)


@receiver(post_save, sender=Repository)
def create_on_disk_repository(sender, instance, created, **kwargs):
    if created:
        if instance.task_id is not None:
            logger.warning("task_id was already set...")
        instance.task_id = setup_repo.delay(instance)
        instance.save()


@receiver(post_delete, sender=Repository)
def archive_repository_on_delete(sender, instance, **kwargs):
    archive_old_repository.delay(instance)
