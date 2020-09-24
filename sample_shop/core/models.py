from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify
from model_utils.models import TimeStampedModel

class AbstractPage(MPTTModel):
    name = models.CharField('Название страницы', max_length=255, default='')
    slug = models.SlugField('URL', max_length=255, blank=True, default='')
    url = models.CharField('Полный адрес', max_length=255, blank=True, default='')
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Страница родителя',
    )
    title = models.CharField('Содержимое тега title', max_length=255, blank=True, default='')
    description = models.CharField('Содержимое тега description', max_length=255, blank=True, default='')
    is_published = models.BooleanField('Опубликована', default=True)
    published_at = models.DateTimeField('Дата публикации', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего изменения', auto_now=True)
    content = RichTextField('Содержание', blank=True, default='')

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
        unique_together = ('parent', 'slug')
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_published:
            self.published_at = now()
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @classmethod
    def page_viewname(cls):
        return ''

    def get_path(self):
        return '/'.join([getattr(item, 'slug') for item in self.get_ancestors(include_self=True)]) + '/'

    def update_url(self):
        for i in self.get_descendants() | self.get_ancestors(include_self=True):
            i.url = i.get_path()
            i.save(update_fields=('url',))

    def get_absolute_url(self):
        return reverse(type(self).page_viewname(), kwargs={'path': self.url if self.url else self.get_path()})


class AbstractSettings(models.Model):
    @classmethod
    def get_settings(cls):
        return cls.objects.get_or_create(pk=1)[0]

    def __str__(self):
        return 'Настройки'

    class Meta:
        abstract = True
        verbose_name = 'настройки'
        verbose_name_plural = 'настройки'

class AbstractNavItem(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    link = models.CharField(max_length=255, verbose_name='Ссылка')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class SEOMixin(TimeStampedModel):
    h1 = models.CharField('H1', max_length=250, default='', blank=True)
    title = models.CharField('Заголовок', max_length=250, default='', blank=True)
    keywords = models.CharField('Keywords', max_length=250, default='', blank=True)
    description = models.TextField('Description', default='', blank=True)

    class Meta:
        abstract = True


class MPTTSEOModel(SEOMixin, MPTTModel):
    name = models.CharField('Название', max_length=250, default='')
    slug = models.SlugField('URL', max_length=250, default='', blank=True)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, related_name='children', blank=True, null=True, verbose_name='Родитель'
    )
    url = models.CharField('Полный URL', max_length=255, default='', blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # def get_path(self):
    #     return '/'.join([item.slug for item in self.get_ancestors(include_self=True)]) + '/'
    #
    # def update_url(self):
    #     for i in self.get_descendants() | self.get_ancestors(include_self=True):
    #         i.url = i.get_path()
    #         i.save(update_fields=('url',))
