from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'image',
                    'intro_text',
                    'content',
                    'has_button',
                    'is_active',
                    'is_video_review',
                    'created',
                    'modified',
                )
            },
        ),
        ('SEO', {'fields': ('seo_title', 'seo_description')}),
    )
    readonly_fields = ('created', 'modified')
