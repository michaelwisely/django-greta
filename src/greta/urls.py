from django.conf.urls.defaults import patterns, url, include

from .views import RepositoryList


urlpatterns = patterns(
    '',
    url(r'^$',
        RepositoryList.as_view(),
        name='repo_list'),

    url(r'^', include('greta.repo_view_urls')),

)
