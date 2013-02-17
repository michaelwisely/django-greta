from django.conf.urls.defaults import patterns, url

from .views import (RepositoryList, RedirectToDefaultBranch, RepositoryDetail,
                    CommitDetail, BranchDetail, TagDetail)


urlpatterns = patterns(
    '',
    url(r'^$',
        RepositoryList.as_view(),
        name='repo_list'),
    url(r'^(?P<pk>\d+)/$',
        RedirectToDefaultBranch.as_view(),
        name='repo_detail'),
    url(r'^(?P<pk>\d+)/branches/$',
        BranchDetail.as_view(),
        name='branch_detail'),
    url(r'^(?P<pk>\d+)/tags/$',
        TagDetail.as_view(),
        name='tag_detail'),
    # url(r'^(?P<pk>\d+)/(?P<ref>.+)/tree/(?P<path>.+)/$',
    #     RepositoryDetail.as_view(),
    #     name='tree_detail'),
    # url(r'^(?P<pk>\d+)/(?P<ref>.+)/blob/(?P<path>.+)/$',
    #     RepositoryDetail.as_view(),
    #     name='blob_detail'),
    url(r'^(?P<pk>\d+)/(?P<ref>.+)/commit/$',
        CommitDetail.as_view(),
        name='commit_detail'),
    url(r'^(?P<pk>\d+)/(?P<ref>.+)/$',
        RepositoryDetail.as_view(),
        name='repo_detail'),
)
