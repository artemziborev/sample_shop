from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django_mptt_admin.admin import DjangoMpttAdmin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import Page, Advantage, Certificate, FinishedWork, TeamMember, CallBackRequest, TopMenuItem
from .models import MainNavItem, BannersMain, SearchPlaceholder, Subscriber, Manager


@admin.register(Page)
class PageAdmin(DjangoMpttAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'url',
                    'parent',
                    'is_published',
                    'published_at',
                    'created_at',
                    'updated_at',
                    'content',
                    'type',
                    'template_name',
                    'dop_template',
                )
            },
        ),
        ('SEO', {'fields': ('title', 'description')}),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Advantage)
class AdvantageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(Certificate)
class CertificateAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(FinishedWork)
class FinisedWorkAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(TeamMember)
class TeamMemberAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(CallBackRequest)
class CallBackRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(TopMenuItem)
class TopMenuItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(MainNavItem)
class MainNavItemAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(BannersMain)
class BannersMainAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)


@admin.register(SearchPlaceholder)
class SearchPlaceholderAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    pass

@admin.register(Manager)
class ManagerAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('__str__', 'is_active')
    list_editable = ('is_active',)
