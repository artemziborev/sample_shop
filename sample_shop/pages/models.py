from ckeditor.fields import RichTextField
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel

from django.utils.translation import gettext_lazy as _
from sample_shop.core.models import AbstractNavItem
from sample_shop.core.models import AbstractPage


class Page(AbstractPage):
    PAGE_TYPE_STATIC = 0
    PAGE_TYPE_CATEGORY = 1
    PAGE_TYPE_CHOICES = ((PAGE_TYPE_STATIC, _('Статическая страница')), (PAGE_TYPE_CATEGORY, _('Страница каталога')))

    type = models.PositiveSmallIntegerField(
        choices=PAGE_TYPE_CHOICES, default=PAGE_TYPE_STATIC, verbose_name=_('Тип страницы')
    )
    template_name = models.CharField(
        _('Название пользовательского шаблона страницы'), max_length=100, blank=True, null=True
    )
    dop_template = models.CharField(_('Допoлнительный HTML контент'), max_length=150, default='', blank=True)

    @classmethod
    def page_viewname(cls):
        return 'pages:page'


class Advantage(models.Model):
    image = models.FileField(upload_to='advantages', verbose_name=_('Иконка'))
    first_title = models.CharField(max_length=255, verbose_name=_('Первый заголовок'))
    second_title = models.CharField(verbose_name=_('Второй заголовок'), max_length=50)
    text = models.TextField(_('Текст'), default='')
    is_active = models.BooleanField(_('Активен'), default=True)
    order = models.PositiveSmallIntegerField(_('Порядок'), default=0)

    def __str__(self):
        return self.first_title

    class Meta:
        verbose_name = _('Преимущество')
        verbose_name_plural = _('Преимущества')
        ordering = ['order']


class Certificate(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование сертификата')
    image = models.ImageField(upload_to='certificates', verbose_name='Фото сертификата')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.SmallIntegerField(verbose_name='Порядок отображения', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        ordering = ['order']


class FinishedWork(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    image = models.ImageField(upload_to='finished_works', verbose_name='Фото работы')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.SmallIntegerField(verbose_name='Порядок отображения', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Готовая работа'
        verbose_name_plural = 'Готовые работы'
        ordering = ['order']


class TeamMember(models.Model):
    name = models.CharField(max_length=255, verbose_name=' Имя Фамилия сотрудника')
    position = models.CharField(max_length=255, verbose_name='Должность сотрудника')
    image = models.ImageField(upload_to='team_members', verbose_name='Фото сотрудника')
    order = models.SmallIntegerField(verbose_name='Порядок отображения', default=0)
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['order']


class SEO(models.Model):
    page_title = models.CharField(max_length=255, verbose_name='Содержимое тега Title')
    page_decription = models.CharField(max_length=255, verbose_name='Содержимое тега Description')
    seo_text_1 = RichTextField('SEO текст 1', blank=True, default='')
    seo_text_2 = RichTextField('SEO текст 2', blank=True, default='')


class CallBackRequest(models.Model):
    """
    Форма "Заказать звонок" на главной странице
    """

    FORM_TYPE_CALLBACK = '1'
    FORM_TYPE_CONTACT_US = '2'
    FORM_TYPE_COOP = '3'
    FORM_TYPES = ((FORM_TYPE_CALLBACK, 'Форма обратной связи'),
                  (FORM_TYPE_CONTACT_US, 'Связаться с нами'),
                  (FORM_TYPE_COOP, 'Хотите сотрудничать'))
    form_type = models.CharField("Тип формы", choices=FORM_TYPES, default=FORM_TYPE_CALLBACK, max_length=1)

    name = models.CharField('Имя', max_length=255)
    email = models.EmailField('E-mail', blank=True)
    phone = models.CharField('Телефон', max_length=15, validators=[MinLengthValidator(11), MaxLengthValidator(11)],
                             blank=True)
    message = models.TextField('Текст сообщения', blank=True)

    def __str__(self):
        return f'{self.email}   {self.phone}'

    class Meta:
        verbose_name = 'ФОС Заказать звонок'
        verbose_name_plural = 'ФОС Заказать звонок'


class TopMenuItem(AbstractNavItem):
    class Meta:
        verbose_name = 'Раздел верхнего меню'
        verbose_name_plural = 'Разделы верхнего меню'
        ordering = ['order']


class MainNavItem(AbstractNavItem):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    image = models.FileField(upload_to='main_nav', verbose_name='Картинка', default='')
    link = models.CharField(max_length=255, verbose_name='Ссылка')
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'Раздел основной навигации'
        verbose_name_plural = 'Разделы основной навигации'
        ordering = ['order']


class BannersMain(models.Model):
    name = models.CharField('Название баннера', max_length=255, default='')
    image_desktop = models.ImageField('Баннер десктопа', upload_to='main_banner', blank=True)
    image_mobile = models.ImageField('Баннер мобильный', upload_to='main_banner_mobile', blank=True)
    title = models.CharField('Заголовок баннера', max_length=255, default='', blank=True)
    text = models.CharField('Текс баннера', max_length=255, default='', blank=True)
    link = models.CharField('Ссылка с баннера', max_length=255, default='', blank=True)
    is_active = models.BooleanField('Показывать', default=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = 'Баннер на главной странице'
        verbose_name_plural = 'Баннеры на главной странице'
        ordering = ['order']


class SearchPlaceholder(models.Model):
    text = models.CharField('Текст', max_length=250, default='', unique=True)
    is_active = models.BooleanField('Активный', default=True)

    class Meta:
        verbose_name = 'Текст для строки поиска'
        verbose_name_plural = 'Тексты для строки поиска'
        ordering = ('text',)

    def __str__(self):
        return self.text


class Subscriber(models.Model):
    email_address = models.EmailField(unique=True, verbose_name='Email подписчика')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class Manager(models.Model):
    image = models.ImageField('Фото', upload_to='managers_images', blank=True, null=True)
    name = models.CharField('Имя', max_length=256)
    family_name = models.CharField('Фамилия', max_length=255)
    additional_number = models.CharField('Добавочный номер', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=255, blank=True)
    messenger = models.CharField('Мессенджер', max_length=60, blank=True)
    social_network = models.CharField('Социальная сеть', max_length=255, blank=True)
    is_active = models.BooleanField('Активен', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    def __str__(self):
        return self.family_name

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'
        ordering = ['order']
