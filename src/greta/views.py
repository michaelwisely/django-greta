from django.views.generic import ListView, DetailView

from .models import Repository

import logging

logger = logging.getLogger(__name__)


class RepositoryList(ListView):
    model = Repository
    context_object_name = "repos"
    template_name = "greta/repository_list.html"


class RepositoryDetail(DetailView):
    model = Repository
    context_object_name = "repo"
    template_name = "greta/repository_detail.html"


class CommitDetail(DetailView):
    model = Repository
    context_object_name = "repo"
    template_name = "greta/commit_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CommitDetail, self).get_context_data(**kwargs)
        return context
