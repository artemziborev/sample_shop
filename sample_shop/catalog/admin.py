from django.contrib import admin
from . import models
from django_mptt_admin.admin import DjangoMpttAdmin
from sample_shop.products.models import Importer

@admin.register(Importer)
class ImporterAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Category)
class CategoryAdmin(DjangoMpttAdmin):
    pass

@admin.register(models.ImportedCategory)
class ImportedCategoryAdmin(DjangoMpttAdmin):
    search_fields = ('name', 'sync_id')
    fields = ('name', 'parent', 'sync_id', 'equivalent_category', 'created', 'modified')
    readonly_fields = ('name', 'parent', 'sync_id', 'created', 'modified')
