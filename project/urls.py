from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'', include('greta.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'accounts/login/$',
        'django.contrib.auth.views.login',
        name='login'),
    url(r'accounts/logout/$',
        'django.contrib.auth.views.logout_then_login',
        name='logout'),
    )

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
