from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from model_utils.models import TimeStampedModel

from slugify import slugify
from sample_shop.products import models as products_models

from django.db.models import Q, Sum
from sample_shop.core.models import MPTTSEOModel



class Category(MPTTSEOModel):
    name = models.CharField(max_length=255, unique=True, verbose_name='')
    icon = models.ImageField(upload_to='category_images', default='', blank=True, null=True)
    product_count = models.PositiveIntegerField('Колличество товаров в категории', default=0, editable=False)
    parent = TreeForeignKey(
                'self',
                on_delete=models.CASCADE,
            related_name='children',
            null=True,
            blank=True,
            db_index=True,
            verbose_name='Категория родителя',)
    slug = models.SlugField(max_length=250, blank=True, null=True, unique=True)
    order = models.PositiveSmallIntegerField('Порядок сортировки', default=0)



    def __str__(self):
        return self.name if self.name else ''

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def get_product_count(self):
        return (
            products_models.BaseProduct.objects.filter(is_active=False)
            .annotate(full_stock=Sum('sub_product_list__stock'))
            .filter(full_stock__gt=1)
            .filter(
                Q(categories__in=self.get_descendants(include_self=True))
                | Q(manual_categories__in=self.get_descendants(include_self=True))
            )
            .count()
        )

    def get_absolute_url(self):
        return reverse('catalog:category', kwargs={'slug': self.slug })



    class Meta:
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'
        ordering = ['order']


class ImportedCategory(TimeStampedModel, MPTTModel):
    name = models.CharField('Название', max_length=255, default='')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='children', blank=True, null=True,
                            verbose_name='Родительская категория')
    sync_id = models.CharField('ID синхронизации', max_length=255, unique=True, null=True)
    equivalent_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='imported_categories', verbose_name='Эквивалентная категория')

    class Meta:
        verbose_name = 'Импортированная категория'
        verbose_name_plural = 'Импортированные категории'

    def __str__(self):
        return self.name if self.name else ''

class CategoryBanner(models.Model):
    name = models.CharField('Название', max_length=255, default='')
    image = models.ImageField('Изображение', upload_to='category_banners', blank=True)
    title = models.CharField('Заголовок', max_length=255, default='')
    link = models.CharField('Ссылка', max_length=255, default='', blank=True)
    is_active = models.BooleanField('Отображать', default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='')
    order = models.PositiveSmallIntegerField('Порядок отображения', default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'Баннер категорий'
        verbose_name_plural = 'Баннеры категорий'
        ordering = ['order']

    def __str__(self):
        return self.name if self.name else ''


