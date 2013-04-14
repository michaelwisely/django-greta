from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import (RedirectView, ListView, DetailView,
                                  TemplateView)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.conf import settings

from guardian.mixins import PermissionRequiredMixin

from dulwich.objects import Tag, Commit

from .models import Repository
from .utils import is_binary, image_mimetype

import re
import logging

logger = logging.getLogger(__name__)


class GretaMixin(PermissionRequiredMixin, SingleObjectMixin):
    model = Repository
    context_object_name = "repo"
    permission_required = "greta.can_view_repository"
    raise_exception = True
    sha_re = re.compile(r'^[a-f0-9]{40}$')

    def dispatch(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = args[0]
        return super(GretaMixin, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        # Check if the repo is ready
        if not self.get_object().is_ready():
            context = RequestContext(self.request, {})
            return render_to_response("greta/repository_not_ready.html",
                                      context)
        self.validate_ref(self.kwargs['ref'])
        return super(GretaMixin, self).get(*args, **kwargs)

    def validate_ref(self, ref):
        sha_match = self.sha_re.match(ref)
        if sha_match is not None:
            # If it's a valid sha1 hash, we're good.
            return

        repo = self.get_object()
        if not ref.startswith('refs'):
            # If it doesn't start with 'refs/heads, we'll assume it's
            # a branch name.
            ref = 'refs/heads/' + ref
        if ref in repo.repo.get_refs():
            # If it's in the list of refs, we're solid.
            return

        # If the repo's empty, let them through
        if len(repo.repo.get_refs()) == 0:
            return

        # If we haven't returned yet, the ref must be no good.
        logger.debug('Invalid ref: "%s"' % ref)
        raise Http404("No such ref.")

    def update_ref(self):
        default_ref = 'refs/heads/' + self.object.default_branch
        current_ref = self.request.session.get('current_ref', default_ref)

        new_ref = self.request.GET.get('ref', None)

        if new_ref in self.object.repo.get_refs():
            current_ref = new_ref

        self.request.session['current_ref'] = current_ref

    def get_context_data(self, **kwargs):
        context = super(GretaMixin, self).get_context_data(**kwargs)

        # add current_ref and ref_type to user's session
        self.update_ref()

        # Add ref to contect
        context['ref'] = self.kwargs['ref']

        return context


class RepositoryList(ListView):
    model = Repository
    context_object_name = "repos"
    template_name = "greta/repository_list.html"


class RedirectToDefaultBranch(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            self.request.session.pop('current_ref')
        except KeyError:
            pass
        repo = get_object_or_404(Repository, pk=self.kwargs['pk'])
        return repo.get_absolute_url()


class RepositoryDetail(GretaMixin, DetailView):
    template_name = "greta/repository_detail.html"
    paginate_commits_by = getattr(settings, "GRETA_PAGE_COMMITS_BY", 10)

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)

        try:
            commits = self.object.get_log(ref=self.kwargs['ref'])
        except KeyError:
            raise Http404("Bad ref")

        paginator = Paginator(commits, self.paginate_commits_by)
        page = self.request.GET.get('page', None)
        try:
            context['log'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['log'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page
            # of results.
            context['log'] = paginator.page(paginator.num_pages)

        return context


class CommitDetail(GretaMixin, DetailView):
    template_name = "greta/commit_detail.html"

    def get_context_data(self, **kwargs):
        context = super(CommitDetail, self).get_context_data(**kwargs)
        try:
            repo = self.object
            context['changes'] = repo.show(self.kwargs['ref'])
            context['commit'] = repo.get_commit(self.kwargs['ref'])

            # Find tags that point to this commit
            # tag_dict maps tag names ('refs/tags/...') to sha's
            tag_dict = repo.repo.refs.as_dict()
            context['tags'] = []
            for tag, tag_id in [(t, tag_dict[t]) for t in repo.tags]:
                obj, obj_id = repo.repo[tag_id], None
                if isinstance(obj, Tag):
                    _, obj_id = obj.object
                if isinstance(obj, Commit):
                    obj_id = obj.id
                if context['commit'].id == obj_id:
                    context['tags'].append((tag, obj))
        except KeyError:
            raise Http404("Bad ref")
        return context


class TreeDetail(GretaMixin, DetailView):
    template_name = "greta/tree_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TreeDetail, self).get_context_data(**kwargs)
        try:
            context['path'] = self.kwargs['path']
            context['tree'] = self.object.get_tree(self.kwargs['ref'],
                                                   self.kwargs['path'])
            context['commit'] = self.object.get_commit(self.kwargs['ref'])
        except KeyError:
            raise Http404("Bad ref")
        except AttributeError:
            raise Http404("Cannot view blob as a tree")

        return context


class BlobDetail(GretaMixin, DetailView):
    template_name = "greta/blob_detail.html"

    def get_context_data(self, **kwargs):
        context = super(BlobDetail, self).get_context_data(**kwargs)
        try:
            path = self.kwargs['path']
            blob = self.object.get_blob(self.kwargs['ref'], path)
            blob_contents = blob.as_raw_string()

            context['path'] = path
            context['blob'] = blob
            context['blob_contents'] = blob_contents
            context['blob_is_binary'] = is_binary(blob_contents)
            context['blob_is_image'] = image_mimetype(path)
            context['commit'] = self.object.get_commit(self.kwargs['ref'])
        except KeyError:
            raise Http404("Bad ref")
        return context


class ImageBlobDetail(GretaMixin, View):

    def get(self, *args, **kwargs):
        try:
            obj = self.get_object()
            mimetype = image_mimetype(kwargs['path'])
            if mimetype is None:
                raise Http404("%s is not an image" % kwargs['path'])

            blob = obj.get_blob(kwargs['ref'], kwargs['path'])
            return HttpResponse(blob.as_raw_string(), content_type=mimetype)
        except KeyError:
            raise Http404("Bad ref")
        return context
