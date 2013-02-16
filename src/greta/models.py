from django.db import models
from django.conf import settings

from .validators import repo_name_validator

from dulwich.repo import Repo as DulwichRepo

import os


def path_to_list(path):
    head, tail = os.path.split(path)
    if head in ('', '/') and tail == '':
        return ()
    return path_split(head) + (tail,)



class Repository(models.Model):
    root_dir = settings.GRETA_ROOT_DIR
    repo_name = models.CharField(max_length=100,
                                 validators=[repo_name_validator])

    def __init__(self, *args, **kwargs):
        self._dulwich_repo = None
        super(Repository, self).__init__(*args, **kwargs)

    @property
    def path(self):
        return os.path.join(self.root_dir, self.repo_name)

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


