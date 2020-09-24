from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.HappyGiftsReport)
class HappyGiftsReportAdmin(admin.ModelAdmin):
    pass
