from django.views.generic import ListView, DetailView

from .models import Repository


class RepositoryList(ListView):
    model = Repository
    context_object_name = "repos"
    template_name = "greta/repository_list.html"
