# Generated by Django 3.0.9 on 2020-08-13 06:09

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FullReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
            ],
            options={
                'verbose_name': 'Отчет',
                'verbose_name_plural': 'Отчеты',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='HappyGiftsReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('count_base_product_in_parser', models.PositiveIntegerField(default=0, verbose_name='Количество базовых товаров у поставщика')),
                ('count_base_product_update', models.PositiveIntegerField(default=0, verbose_name='Количество обновленных базовых товаров')),
                ('count_base_product_create', models.PositiveIntegerField(default=0, verbose_name='Количество созданных базовых товаров')),
                ('count_sub_product_in_parser', models.PositiveIntegerField(default=0, verbose_name='Количество под-товаров у поставщика')),
                ('count_sub_product_update', models.PositiveIntegerField(default=0, verbose_name='Количество обновленных под-товаров')),
                ('count_sub_product_create', models.PositiveIntegerField(default=0, verbose_name='Количество созданных под-товаров')),
                ('count_sub_product_without_price', models.PositiveIntegerField(default=0, verbose_name='Количество под-товаров без цены')),
                ('sub_product_without_price_id_list', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, default=list, size=None, verbose_name='Список под-товаров без цены')),
                ('count_sub_product_without_image', models.PositiveIntegerField(default=0, verbose_name='Количество под-товаров без изображений')),
                ('sub_product_without_image_id_list', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), blank=True, default=list, size=None, verbose_name='Список под-товаров без изображений')),
                ('parent', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='happy_gifts', to='parsers.FullReport')),
            ],
            options={
                'verbose_name': 'Отчёт Happy Gifts',
                'verbose_name_plural': 'Отчёт Happy Gifts',
            },
        ),
    ]
