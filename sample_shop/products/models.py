from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from mptt.models import TreeManyToManyField
from jsoneditor.fields.postgres_jsonfield import JSONField
from slugify import slugify
from sample_shop.utils.utils import get_unique_slug_for_model



class Importer(models.Model):
    name = models.CharField('Поставщик', max_length=255, blank=True, null=True)
    coefficient = models.PositiveSmallIntegerField('Коэффициент', default=100)

    def __str__(self):
        return self.name if self.name else ''

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование бренда', default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField('', default='', blank=True, null=True)
    icon = models.FileField(upload_to='brands_icons', verbose_name='Картинка бренда', blank=True, null=True)
    # tags = models.ManyToManyField(Tag, related_name=brands)
    importer = models.ManyToManyField(Importer, related_name='importers', verbose_name='Поставщики')
    is_active = models.BooleanField('Активен', default=True)
    coefficient = models.PositiveSmallIntegerField('Коэффициент', default=0, blank=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Brand, self).save(*args, **kwargs)



# class Tag(models.Model):
#     name = models.CharField('', max_length=255, blank=True, null=True)
#
#     class Meta:
#         verbose_name = ''
#         verbose_name_plural = ''
#         ordering = ('name',)


class Color(models.Model):
    name = models.CharField('Название цвета', max_length=255, default='', unique=True)
    hex_name = models.CharField('HEX обозначение цвета', max_length=255, default='', blank=True)

    class Meta:
        verbose_name = ' Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''


class Size(models.Model):
    name = models.CharField('Название размера', max_length=255, default='', unique=True)
    order = models.PositiveIntegerField('', default=0)

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'
        ordering =('order',)

    def __str__(self):
        return self.name if self.name else ''


class Material(models.Model):
    name = models.CharField('Название материала', max_length=255, default='', unique=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ('name', )

    def __str__(self):
        return self.name if self.name else ''


class Collection(models.Model):
    name = models.CharField('Название', max_length=255, default='')
    importer = models.ForeignKey(Importer, on_delete=models.CASCADE, related_name='collections', verbose_name='Поставщик')

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''


class Print(models.Model):
    name = models.CharField('Название', max_length=255, default='', unique=True)

    class Meta:
        verbose_name = 'Тип нанесения'
        verbose_name_plural = 'Типы нанесения'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''


class BaseProduct(models.Model):
    # MALE =
    # FEMALE =
    #SEX_CHOICES
    DEFAULT_SORT = '-popularity'
    name = models.CharField('Наименование', max_length=255, default='')
    categories = TreeManyToManyField('catalog.Category', related_name='base_products_list', blank=True, verbose_name='Категории')
    manual_categories = TreeManyToManyField('catalog.Category', related_name='manual_base_product_list',
                                            blank=True, verbose_name=' Категории добавленные вручную')
    remote_id = models.CharField('ID синхронизации', max_length=255, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name='products_list', blank=True, null=True)
    article = models.CharField('Артикул',max_length=255, default='', blank=True, null=True)
    colors = models.ManyToManyField(Color, related_name='products_list', blank=True, verbose_name='Цвета')
    sex = models. CharField('Пол', max_length=255, default='', blank=True) #choises = SEX_CHOICES
    materials = models.ManyToManyField(Material, related_name='product_list', blank=True, verbose_name='Материалы')
    prints = models.ManyToManyField(Print, related_name='product_list')
    attributes = JSONField('Дополнительные характеристики', default=dict, blank=True)
    is_sublimation = models.BooleanField('Сублимация', default=False)
    is_active = models.BooleanField('Активен', default=True)
    is_new = models.BooleanField('Новинка', default=False)
    importer = models.ForeignKey(Importer, on_delete=models.SET_NULL, related_name='product_list', null=True, verbose_name='Поставщик') #TODO возможно стоит заменить на  M2M
    popularity = models.PositiveIntegerField('Популярность', default=0, blank=True)

    class Meta:
        verbose_name = 'Базовый товар'
        verbose_name_plural = 'Базовые товары'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''

class SubProduct(models.Model):
    base_product = models.ForeignKey(BaseProduct, related_name='sub_product_list', verbose_name='Базовый товар',
                                     on_delete=models.CASCADE)
    name = models.CharField('Наименование', max_length=255,blank=True, default='')
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    remote_id = models.CharField('Базовый ID синхронизации', max_length=255, unique=True)
    old_price = models.DecimalField('Цена без скидки', max_digits=10, decimal_places=2, default=0, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0, blank=True)
    article = models.CharField('Артикул', max_length=255, default='', blank=True)
    group_id = models.CharField('ID товарной группы', max_length=255, default='', blank=True)
    main = models.BooleanField('Основной товар', default=False)
    content = models.TextField('Описание', default='', blank=True)
    stock = models.PositiveIntegerField('Остаток на складе', default=0, blank=True)
    size = models.ForeignKey(
        'Size', on_delete=models.SET_NULL, related_name='sub_product_list', blank=True, null=True, verbose_name='Размер'
    )
    colors = models.ManyToManyField('Color', related_name='sub_product_list', blank=True, verbose_name='Цвета')

    class Meta:
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товара'
        ordering = ('name',)

    def __str__(self):
        return self.name if self.name else ''

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug_for_model(self.name, SubProduct)
        super().save(*args, **kwargs)



class Image(TimeStampedModel):
    product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name='images', verbose_name='Продукт')
    image = models.ImageField('Изобажение', upload_to='products_images', default='', blank=True)
    remote_url = models.CharField('Ссылка', max_length=250, default='', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    main_image = models.BooleanField('Главное изображение', default=False)

    class Meta:
        verbose_name = 'Изображение продукта'
        verbose_name_plural = 'Изображения продукта'
        ordering = ('product', '-main_image')

    def __str__(self):
        return f'Изображение продукта {self.product}'


class ProductFile(models.Model):
    product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, verbose_name='Товар')
    file = models.FileField(upload_to='product_files', blank=True, null=True, verbose_name='файл_продукта')
    base_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField('Название', max_length=255, default='')

    class Meta:
        verbose_name = 'Файл продукта'
        verbose_name_plural = 'Файлы продукта'

    def __str__(self):
        return f'Файл {self.file} товара {self.product}' if self.file else ''




