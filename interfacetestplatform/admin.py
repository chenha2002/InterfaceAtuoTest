
from django.contrib import admin
from .import models


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "proj_owner", "test_owner", "dev_owner", "desc", "create_time", "update_time")

admin.site.register(models.Project, ProjectAdmin)

class ModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "desc", "create_time", "update_time")

admin.site.register(models.Model, ModelAdmin)