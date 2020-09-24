from django.db import models
from django.contrib.postgres.fields import ArrayField
from model_utils.models import TimeStampedModel


class FullReport(TimeStampedModel):
    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'
        ordering = ('-created',)

    def __str__(self):
        return 'Отчет №{}'.format(self.id)

    def get_report_list(self):
        return [
            getattr(self, x)
            for x in ['happy_gifts']
            if hasattr(self, x)
        ]

class ReportAbstract(TimeStampedModel):
    count_base_product_in_parser = models.PositiveIntegerField('Количество базовых товаров у поставщика', default=0)
    count_base_product_update = models.PositiveIntegerField('Количество обновленных базовых товаров', default=0)
    count_base_product_create = models.PositiveIntegerField('Количество созданных базовых товаров', default=0)
    count_sub_product_in_parser = models.PositiveIntegerField('Количество под-товаров у поставщика', default=0)
    count_sub_product_update = models.PositiveIntegerField('Количество обновленных под-товаров', default=0)
    count_sub_product_create = models.PositiveIntegerField('Количество созданных под-товаров', default=0)

    count_sub_product_without_price = models.PositiveIntegerField('Количество под-товаров без цены', default=0)
    sub_product_without_price_id_list = ArrayField(
        models.PositiveIntegerField(), verbose_name='Список под-товаров без цены', default=list, blank=True
    )
    count_sub_product_without_image = models.PositiveIntegerField('Количество под-товаров без изображений', default=0)
    sub_product_without_image_id_list = ArrayField(
        models.PositiveIntegerField(), verbose_name='Список под-товаров без изображений', default=list, blank=True
    )

    class Meta:
        abstract = True

    @property
    def count_base_product(self):
        return self.count_base_product_update + self.count_base_product_create

    @property
    def count_sub_product(self):
        return self.count_sub_product_update + self.count_sub_product_create

class HappyGiftsReport(ReportAbstract):
    parent = models.OneToOneField(
        FullReport, on_delete=models.CASCADE, related_name="happy_gifts", blank=True, null=True
    )

    class Meta:
        verbose_name = 'Отчёт Happy Gifts'
        verbose_name_plural = 'Отчёт Happy Gifts'

    def __str__(self):
        return f'Отчет Happy Gifts от {self.created}'
