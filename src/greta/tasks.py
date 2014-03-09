from celery import task
from dulwich.repo import Repo as DulwichRepo
from dulwich.errors import NotGitRepository
from celery.result import AsyncResult

from .utils import archive_directory, archive_repository

import celery
import os
import logging
import models

logger = logging.getLogger(__name__)


@task()
def add(x, y):
    return x + y


@task(ignore_result=True)
def setup_repo(repo_pk):
    instance = models.Repository.objects.get(pk=repo_pk)

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
        parent = instance.forked_from
        # Make sure the repo we're forking from exists
        if not parent.created_on_disk:
            msg = "{}'s parent repository is not on disk yet..."
            logger.error(msg.format(instance.name))

        # Clone from the parent
        logger.info("Cloning repo to %s", instance.path)
        parent.repo.clone(instance.path, mkdir=False, bare=True)
        logger.info("Cloned repo to %s", instance.path)
    else:
        # If we're not forking a repo, just init a new one
        logger.info("Initializing repo at %s", instance.path)
        DulwichRepo.init_bare(instance.path)
        logger.info("Initialized repo at %s", instance.path)

    # Set a lock indicating that the list of forks is set
    instance.created_on_disk = True
    instance.save()

    if instance.forks.exists():
        logger.info("Seting up forks of {}".format(instance.name))
        # Assemble the group and call it to start it
        celery.group([setup_repo.s(r.pk) for r in instance.forks.all()])()


@task(ignore_result=True)
def archive_old_repository(repo_pk):
    instance = models.Respository.objects.get(pk=repo_pk)

    if os.path.exists(instance.path):
        archive_repository(instance)
