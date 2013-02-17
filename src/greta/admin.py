from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Repository


class RepositoryAdmin(GuardedModelAdmin):
    pass


admin.site.register(Repository, RepositoryAdmin)
