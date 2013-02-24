from django.conf import settings

import subprocess
import mimetypes
import tempfile
import datetime
import tarfile
import shutil
import os
import re

DIFF_LINE_RE = re.compile(r'^(diff --git .*)$', flags=re.MULTILINE)

import logging
logger = logging.getLogger(__name__)


def time_filename():
    """Returns a time format suitable for a filename"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d--%H-%M-%S-%f")


def archive_directory(path, archive_name=None):
    """Archives a directory at ``path`` using tar, names it
    ``archive_name``, stores it in GRETA_ARCHIVE_DIR, and deletes the
    original path at ``path``"""
    temp_dir = tempfile.mkdtemp(prefix="GRETA_")  # Create a temporary directory
    shutil.move(path, temp_dir)                   # Move the old directory there
    path = os.path.join(temp_dir, os.path.basename(path))
    if archive_name is None:
        archive_name = "{0}.tar.gz".format(time_filename())
    archive_path = os.path.join(settings.GRETA_ARCHIVE_DIR, archive_name)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(path, arcname=os.path.basename(path))


def archive_repository(repo):
    """Archives a repository using tar, stores it in
    GRETA_ARCHIVE_DIR, and deletes the original repository from
    GRETA_REPO_DIR"""
    archive_name = "{0}-{1}-{2}.tar.gz".format(repo.id,
                                               repo.name.replace('/', '-'),
                                               time_filename())
    archive_directory(repo.path, archive_name)


class Commiterator(object):
    line_re = re.compile(r'^([a-f0-9]+)(?: \((.*)\))?$')

    def __init__(self, repo, ref=None, skip=0, max_count=-1):
        command = ['git', 'log', '--format=%H%d',
                   "--skip={0}".format(skip),
                   "--max-count={0}".format(max_count)]
        if ref is not None:
            command.append(ref)
        git_log = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=repo.path)
        stdout, stderr = git_log.communicate()

        if stderr:
            if 'ambiguous argument' in stderr and 'unknown revision' in stderr:
                logger.warning("Git log error: %s", stderr)

        self.commit_shas = stdout.splitlines()
        self.repo = repo

    def process_line(self, line):
        match = self.line_re.match(line)
        sha = match.group(1)
        refs = match.group(2)
        if refs is not None:
            refs = [ref.strip() for ref in refs.split(',')]
        return (self.repo[sha], refs)

    def __len__(self):
        return len(self.commit_shas)

    def __getitem__(self, index_or_slice):
        lines = self.commit_shas[index_or_slice]
        if isinstance(lines, list):
            return [self.process_line(line) for line in lines]
        return self.process_line(lines)

    def __iter__(self):
        for commit in self.commit_shas:
            yield self.repo[commit]


PRINTABLE_CHARS = re.compile(r'(\n|\r|\t|[\x20-\x7e])')
NULL_CHAR = re.compile(r'[\x00]')


def is_binary(string):
    if string == "":
        return False

    # If it contains a NULL, it's binary.
    if NULL_CHAR.search(string) is not None:
        return True

    # Count the number of printable characters
    _, num_printable = PRINTABLE_CHARS.subn('', string)

    # If less than 75% of the characters are printable, it's binary.
    if float(num_printable) / len(string) < 0.75:
        return True

    return False


def image_mimetype(path):
    mimetype, _ = mimetypes.guess_type(path)
    if mimetype is not None:
        if mimetype.startswith('image/'):
            return mimetype
    return None


def pairs(lst):
    for i in xrange(0, len(lst), 2):
        yield lst[i:i + 2]


def split_diff(diff_string):
    """Splits a diff into a list of pairs: (file name, diff)"""
    return pairs(DIFF_LINE_RE.split(diff_string)[1:])
