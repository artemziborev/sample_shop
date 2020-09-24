from django.contrib import admin
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

# Register your models here.
admin.site.register(LogEntry)
admin.site.register(Session)
