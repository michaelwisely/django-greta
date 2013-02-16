import subprocess

import logging
logger = logging.getLogger(__name__)


class Commiterator(object):
    def __init__(self, repo, skip=0, max_count=-1):
        command = ['git', 'log', '--format=%H',
                   "--skip={0}".format(skip),
                   "--max-count={0}".format(max_count)]
        git_log = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   cwd=repo.path)
        stdout, stderr = git_log.communicate()

        if stderr:
            logger.warning(stderr)

        self.commit_shas = stdout.splitlines()
        self.repo = repo

    def __len__(self):
        return len(self.commit_shas)

    def __getitem__(self, index_or_slice):
        commit_shas = self.commit_shas[index_or_slice]
        if isinstance(commit_shas, list):
            return [self.repo[sha] for sha in commit_shas]
        return self.repo[commit_shas]

    def __iter__(self):
        for commit in self.commit_shas:
            yield self.repo[commit]
