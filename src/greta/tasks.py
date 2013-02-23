from celery import task
from dulwich.repo import Repo as DulwichRepo
from dulwich.errors import NotGitRepository

from .utils import archive_directory, archive_repository

import os
import logging

logger = logging.getLogger(__name__)


@task()
def add(x, y):
    return x + y


@task()
def setup_repo(instance):
    if os.path.exists(instance.path):
        # If the repository exists, archive it
        logger.warning("Path %s exists. Archiving it.", instance.path)
        archive_directory(instance.path)
        logger.info("Directory archived.")

    # If we have an abc/dev.git repo, create the "abc" directory
    # if necessary
    if '/' in instance.name:
        logger.info("Repository requires a subdirectory")
        if not os.path.exists(os.path.dirname(instance.path)):
            os.mkdir(os.path.dirname(instance.path))
            logger.info("Created parent directory")
        else:
            logger.info("Parent directory exists")

    # Create the path for the repository
    os.mkdir(instance.path)
    logger.info("Created path for repo at %s", instance.path)

    if instance.forked_from is not None:
        # If we're forking a repo, clone from the parent
        logger.info("Cloning repo to %s", instance.path)
        instance.forked_from.repo.clone(instance.path,
                                        mkdir=False, bare=True)
        logger.info("Cloned repo to %s", instance.path)
    else:
        # If we're not forking a repo, just init a new one
        logger.info("Initializing repo at %s", instance.path)
        DulwichRepo.init_bare(instance.path)
        logger.info("Initialized repo at %s", instance.path)


@task()
def archive_old_repository(instance):
    if os.path.exists(instance.path):
        archive_repository(instance)
