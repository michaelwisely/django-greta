from django.conf.urls.defaults import patterns, url

from .views import RepositoryList


urlpatterns = patterns(
    '',
    url(r'^$',
        RepositoryList.as_view(),
        name='list_repos'),
)
