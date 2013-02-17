from django.views.generic import RedirectView, ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.http import Http404

from guardian.mixins import PermissionRequiredMixin

from .models import Repository

import logging

logger = logging.getLogger(__name__)


class GretaMixin(PermissionRequiredMixin, SingleObjectMixin):
    model = Repository
    context_object_name = "repo"
    permission_required = "greta.can_view_repository"
    raise_exception = True

    def dispatch(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return super(GretaMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GretaMixin, self).get_context_data(**kwargs)
        context['ref'] = self.kwargs['ref']
        return context


class RepositoryList(ListView):
    model = Repository
    context_object_name = "repos"
    template_name = "greta/repository_list.html"


class RedirectToDefaultBranch(RedirectView):
    def get_redirect_url(self, **kwargs):
        repo = get_object_or_404(Repository, pk=self.kwargs['pk'])
        return repo.get_absolute_url()


class RepositoryDetail(GretaMixin, DetailView):
    template_name = "greta/repository_detail.html"

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)
        try:
            context['log'] = self.object.get_log(ref=self.kwargs['ref'])
        except KeyError:
            raise Http404("Bad ref")
        return context


class CommitDetail(RepositoryDetail):
    template_name = "greta/commit_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CommitDetail, self).get_context_data(**kwargs)
        try:
            context['changes'] = self.object.show(self.kwargs['ref'])
            context['commit'] = self.object.get_commit(self.kwargs['ref'])
        except KeyError:
            raise Http404("Bad ref")
        return context
