from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from slugify import slugify
from ckeditor.fields import RichTextField
from model_utils.models import TimeStampedModel

class Article(TimeStampedModel):
    name = models.CharField(_('Наименование'), max_length=255, unique=True, default='')
    intro_text = models.TextField(_('Короткий текст'), default='', blank=True)
    slug = models.SlugField(_('URL'), max_length=255, unique=True, null=True, blank=True)
    content = RichTextField(_('Контент'), default='', blank=True)
    image = models.ImageField(_('Изображение'), upload_to='article_image', blank=True, default='')
    is_active = models.BooleanField(_('Отображать'), default=True)
    seo_title = models.CharField(_('Title'), max_length=255)
    seo_description = models.TextField(_('Description'), default='', blank=True)
    has_button = models.BooleanField(_('Кнопка оформления заявки'))
    is_video_review = models.BooleanField(_('Видеообзор'), default=False)

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        # ordering = ('-date_public',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:article', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_title(self):
        if self.seo_title:
            return self.seo_title
        return f'{self.seo_title} — статьи на'

    def get_description(self):
        if self.seo_description:
            return self.seo_description
        return f'Статья «{self.seo_description}» на'
