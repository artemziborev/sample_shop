# Generated by Django 3.0.9 on 2020-08-13 06:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsoneditor.fields.postgres_jsonfield
import model_utils.fields
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='Наименование')),
                ('remote_id', models.CharField(max_length=255, unique=True, verbose_name='ID синхронизации')),
                ('article', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Артикул')),
                ('sex', models.CharField(blank=True, default='', max_length=255, verbose_name='Пол')),
                ('attributes', jsoneditor.fields.postgres_jsonfield.JSONField(blank=True, default=dict, verbose_name='Дополнительные характеристики')),
                ('is_sublimation', models.BooleanField(default=False, verbose_name='Сублимация')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_new', models.BooleanField(default=False, verbose_name='Новинка')),
                ('popularity', models.PositiveIntegerField(blank=True, default=0, verbose_name='Популярность')),
            ],
            options={
                'verbose_name': 'Базовый товар',
                'verbose_name_plural': 'Базовые товары',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, unique=True, verbose_name='Название цвета')),
                ('hex_name', models.CharField(blank=True, default='', max_length=255, verbose_name='HEX обозначение цвета')),
            ],
            options={
                'verbose_name': ' Цвет',
                'verbose_name_plural': 'Цвета',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Importer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Поставщик')),
                ('coefficient', models.PositiveSmallIntegerField(default=100, verbose_name='Коэффициент')),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, unique=True, verbose_name='Название материала')),
            ],
            options={
                'verbose_name': 'Материал',
                'verbose_name_plural': 'Материалы',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Print',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип нанесения',
                'verbose_name_plural': 'Типы нанесения',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, unique=True, verbose_name='Название размера')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='')),
            ],
            options={
                'verbose_name': 'Размер',
                'verbose_name_plural': 'Размеры',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='SubProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='Наименование')),
                ('slug', models.SlugField(blank=True, max_length=255, null=True, unique=True)),
                ('remote_id', models.CharField(max_length=255, unique=True, verbose_name='Базовый ID синхронизации')),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Цена без скидки')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Цена')),
                ('article', models.CharField(blank=True, default='', max_length=255, verbose_name='Артикул')),
                ('group_id', models.CharField(blank=True, default='', max_length=255, verbose_name='ID товарной группы')),
                ('main', models.BooleanField(default=False, verbose_name='Основной товар')),
                ('content', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('stock', models.PositiveIntegerField(blank=True, default=0, verbose_name='Остаток на складе')),
                ('base_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_product_list', to='products.BaseProduct', verbose_name='Базовый товар')),
                ('colors', models.ManyToManyField(blank=True, related_name='sub_product_list', to='products.Color', verbose_name='Цвета')),
                ('size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_product_list', to='products.Size', verbose_name='Размер')),
            ],
            options={
                'verbose_name': 'Вариант товара',
                'verbose_name_plural': 'Варианты товара',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ProductFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='product_files', verbose_name='файл_продукта')),
                ('base_name', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(default='', max_length=255, verbose_name='Название')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.SubProduct', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Файл продукта',
                'verbose_name_plural': 'Файлы продукта',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('image', models.ImageField(blank=True, default='', upload_to='products_images', verbose_name='Изобажение')),
                ('remote_url', models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='Ссылка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('main_image', models.BooleanField(default=False, verbose_name='Главное изображение')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.SubProduct', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Изображение продукта',
                'verbose_name_plural': 'Изображения продукта',
                'ordering': ('product', '-main_image'),
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='Название')),
                ('importer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='products.Importer', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'Коллекция',
                'verbose_name_plural': 'Коллекции',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='Наименование бренда')),
                ('slug', models.SlugField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, default='', null=True, verbose_name='')),
                ('icon', models.FileField(blank=True, null=True, upload_to='brands_icons', verbose_name='Картинка бренда')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('coefficient', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Коэффициент')),
                ('importer', models.ManyToManyField(related_name='importers', to='products.Importer', verbose_name='Поставщики')),
            ],
            options={
                'verbose_name': 'Бренд',
                'verbose_name_plural': 'Бренды',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products_list', to='products.Brand'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='categories',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='base_products_list', to='catalog.Category', verbose_name='Категории'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='colors',
            field=models.ManyToManyField(blank=True, related_name='products_list', to='products.Color', verbose_name='Цвета'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='importer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_list', to='products.Importer', verbose_name='Поставщик'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='manual_categories',
            field=mptt.fields.TreeManyToManyField(blank=True, related_name='manual_base_product_list', to='catalog.Category', verbose_name=' Категории добавленные вручную'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='materials',
            field=models.ManyToManyField(blank=True, related_name='product_list', to='products.Material', verbose_name='Материалы'),
        ),
        migrations.AddField(
            model_name='baseproduct',
            name='prints',
            field=models.ManyToManyField(related_name='product_list', to='products.Print'),
        ),
    ]
