import csv
import json
import math
import os
import random
import string
from tempfile import TemporaryFile
from typing import Tuple, List
from urllib import request

import requests
from celery.utils.log import get_task_logger
from django.core.files import File
from django.utils import timezone
from slugify import slugify

from sample_shop.catalog.forms import ImportedCategoryForm
from sample_shop.catalog.models import ImportedCategory
from sample_shop.products.models import Importer
from sample_shop.utils.utils import update_categories
from sample_shop.products.forms import ParsedBaseProductForm, ParsedSubProductForm, ImageForm
from sample_shop.products.models import BaseProduct, SubProduct, Image, Color, Size, Brand, Material, ProductFile

logger = get_task_logger('parser')


class BaseParser:
    def __init__(self):
        self.importer, created = ImportedCategory.objects.get_or_create(name=self.parser_name)
        self.product_importer, created = Importer.objects.get_or_create(name=self.parser_name)
        self.report = self.report_class.objects.create()
        self.start_datetime = timezone.now()
        self.base_product_count = 0
        self.base_product_update = 0
        self.base_product_create = 0
        self.sub_product_count = 0
        self.sub_product_update = 0
        self.sub_product_create = 0
        self.sub_product_without_image = 0
        self.sub_product_without_image_id_list = []
        self.sub_product_without_price = 0
        self.sub_product_without_price_id_list = []
        with open('sample_shop/parsers/dop_data/materials.csv') as f:
            self.materials = {x[0]: x[1] for x in csv.reader(f)}
        with open('sample_shop/parsers/dop_data/sex.csv') as f:
            self.sex = {x[0]: x[1] for x in csv.reader(f)}
        with open('sample_shop/parsers/dop_data/prints.csv') as f:
            self.prints = {x[0]: x[1] for x in csv.reader(f)}

    def setup_imported_category(self):
        logger.info('start setup imported category')
        categories = self.get_imported_category()
        count = 0
        full_count = len(categories)
        for category in categories:
            count += 1
            imported_category = None
            if ImportedCategory.objects.filter(sync_id=category['sync_id']).exists():
                imported_category = ImportedCategory.objects.get(sync_id=category['sync_id'])
            form = ImportedCategoryForm(
                {'name': category['name'], 'sync_id': category['sync_id']}, instance=imported_category
            )
            if form.is_valid():
                form.save()
            else:
                logger.warning('Форма не валидная {}'.format(form.errors))
            logger.info('{} from {} cat'.format(count, full_count))
        count = 0
        for category in categories:
            count += 1
            imported_category = ImportedCategory.objects.get(sync_id=category['sync_id'])
            if category['parent_sync_id'] is not None:
                parent_imported_category = ImportedCategory.objects.get(sync_id=category['parent_sync_id'])
                imported_category.parent = parent_imported_category
            else:
                imported_category.parent = self.importer
            imported_category.save()
            logger.info('{} from {} cat'.format(count, full_count))
        ImportedCategory.objects.rebuild()
        update_categories()
        logger.info('finish setup imported category')

    def _get_imported_category(self):
        raise NotImplementedError

    def _dump_imported_categories(self):
        with open('{}_imported_categories.json'.format(self.parser_name), 'w') as f:
            json.dump(self._get_imported_category(), f, indent=2, ensure_ascii=False)

    def get_imported_category(self):
        return self._get_imported_category()

    def _download_ftp_image(self, obj, image):
        with TemporaryFile() as tf:
            try:
                tf.write(request.urlopen(image).read())
                tf.seek(0)
                obj.image.save(self._make_new_name(image), File(tf))
            except request.HTTPError:
                obj.delete()

    def _download_http_image(self, obj, image):
        with TemporaryFile() as tf:
            try:
                res = requests.get(image)
                if res.status_code == 200:
                    tf.write(res.content)
                    tf.seek(0)
                    obj.image.save(self._make_new_name(image), File(tf))
                else:
                    obj.delete()
            except requests.ConnectionError:
                obj.delete()
                logger.error('ConnectionError')

    def _create_image(self, product, image, i):
        form = ImageForm({'product': product.id, 'remote_url': self.generate_sync_id(image), 'main_image': i == 0})
        if form.is_valid():
            print(f'Создаю картинку товара   {self}')
            obj = form.save()
            if image[:3] == 'ftp':
                self._download_ftp_image(obj, image)
            else:
                self._download_http_image(obj, image)
        else:
            logger.warning('Форма изображения не валидная {}'.format(form.errors))

    def _update_image(self, product, image, i):
        form = ImageForm(
            {'product': product.id, 'remote_url': self.generate_sync_id(image), 'main_image': i == 0},
            instance=Image.objects.get(product=product, remote_url=self.generate_sync_id(image)),
        )
        if form.is_valid():
            form.save()
        else:
            logger.warning('Форма изображения не валидная {}'.format(form.errors))

    def setup_imported_image(self, product, image, i):
        if not Image.objects.filter(remote_url=self.generate_sync_id(image), product=product).exists():
            self._create_image(product, image, i)
        else:
            self._update_image(product, image, i)

    def setup_imported_images(self, product, images):
        print('Setup Imported Images')
        for i, image in enumerate(images):
            self.setup_imported_image(product, image, i)
        Image.objects.filter(product=product, modified__lt=self.start_datetime).delete()

    def _get_info_sub_product_without_price(self, sub_product_data_list: List[dict]) -> Tuple[int, list]:
        id_list = [
            SubProduct.objects.get(remote_id=sub_product_data['remote_id']).id
            for sub_product_data in sub_product_data_list
            if sub_product_data['price'] == 0
        ]
        return len(id_list), id_list

    def _setup_product_without_image(self, sub_product_data_list: List[dict]) -> Tuple[int, list]:
        id_list = [
            SubProduct.objects.get(remote_id=sub_product_data['remote_id']).id
            for sub_product_data in sub_product_data_list
            if not len(sub_product_data['images'])
        ]
        return len(id_list), id_list

    def _setup_sub_product(self, sub_product_data, product):
        sub_product_instance = SubProduct.objects.filter(remote_id=sub_product_data['remote_id']).first()

        if sub_product_instance:
            self.sub_product_update += 1
        else:
            self.sub_product_create += 1

        sub_product_data['base_product'] = product.id
        sub_product_data['old_price'], sub_product_data['price'] = self._prepare_price(
            sub_product_data['price'], product
        )
        sub_product_data['colors'] = self._get_colors(sub_product_data['colors'])

        if sub_product_data['size']:
            size, created = Size.objects.get_or_create(name=sub_product_data['size'])
            sub_product_data['size'] = size.id

        sub_form = ParsedSubProductForm(sub_product_data, instance=sub_product_instance)
        if sub_form.is_valid():
            obj = sub_form.save()
            self.setup_imported_images(obj, sub_product_data['images'])
            self.setup_product_file_list(obj, sub_product_data['file_list'])

    def _setup_sub_products(self, sub_product_data_list, product):
        self.sub_product_count += len(sub_product_data_list)
        for sub_product_data in sub_product_data_list:
            self._setup_sub_product(sub_product_data, product)

        count_without_price, id_list_without_price = self._get_info_sub_product_without_price(sub_product_data_list)
        self.sub_product_without_price += count_without_price
        self.sub_product_without_price_id_list += id_list_without_price

        count_without_image, id_list_without_image = self._setup_product_without_image(sub_product_data_list)
        self.sub_product_without_image += count_without_image
        self.sub_product_without_image_id_list += id_list_without_image

    def _setup_report(self):
        self.report.count_base_product_in_parser = self.base_product_count
        self.report.count_base_product_update = self.base_product_update
        self.report.count_base_product_create = self.base_product_create
        self.report.count_sub_product_in_parser = self.sub_product_count
        self.report.count_sub_product_update = self.sub_product_update
        self.report.count_sub_product_create = self.sub_product_create
        self.report.count_sub_product_without_price = self.sub_product_without_price
        self.report.sub_product_without_price_id_list = self.sub_product_without_price_id_list
        self.report.count_sub_product_without_image = self.sub_product_without_image
        self.report.sub_product_without_image_id_list = self.sub_product_without_image_id_list
        self.report.save()

    def _setup_brand(self, brand_name: str):
        brand_name = brand_name.lower()
        brand, created = Brand.objects.get_or_create(name=brand_name)
        if created:
            brand_slug = slugify(brand_name)
            c = 0
            while Brand.objects.filter(slug=brand_slug).exists():
                c += 1
                brand_slug = f'{brand_slug}{c}'
            brand.slug = brand_slug
            brand.save()
        return brand

    def setup_imported_products(self):
        products = self._get_imported_products()
        self.base_product_count = len(products)
        self._setup_colors(products)
        print('Setting up colors')
        self._setup_materials(products)
        print('Setting up materials')
        for product_data in products:
            base_product_instance = BaseProduct.objects.filter(remote_id=product_data['remote_id']).first()
            if base_product_instance:
                self.base_product_update += 1
            else:
                self.base_product_create += 1

            if 'brand' in product_data and product_data['brand'] is not None:
                product_data['brand'] = self._setup_brand(product_data['brand']).id

            product_data['categories'] = self._get_categories(product_data['categories'])
            product_data['colors'] = self._get_colors(product_data['colors'])
            product_data['materials'] = self._get_materials(product_data['materials'])
            product_data['importer'] = self.product_importer.id

            form = ParsedBaseProductForm(product_data, instance=base_product_instance)
            if form.is_valid():
                product = form.save()
                self._setup_sub_products(product_data['sub_product_data_list'], product)
        SubProduct.objects.filter(
            modified__lt=self.start_datetime, base_product__importer=self.product_importer
        ).delete()
        BaseProduct.objects.filter(modified__lt=self.start_datetime, importer=self.product_importer).delete()
        Image.objects.filter(image='').delete()
        self._setup_report()
        update_categories()
        return True

    def _get_imported_products(self):
        raise NotImplementedError

    def _dump_imported_products(self):
        with open('{}_imported_products.json'.format(self.parser_name), 'w') as f:
            json.dump(self._get_imported_products(), f, indent=2, ensure_ascii=False)

    def update_stock(self):
        products = self._get_imported_products()
        for product_data in products:
            for sub_product_data in product_data['sub_product_data_list']:
                try:
                    p = SubProduct.objects.get(remote_id=sub_product_data['remote_id'])
                    p.stock = sub_product_data['stock']
                    p.save()
                except SubProduct.DoesNotExist:
                    pass

    def generate_sync_id(self, _id: str) -> str:
        return '{}_{}'.format(self.parser_name, _id)

    def setup_product_file_list(self, product, file_list):
        for file in file_list:
            self.setup_product_file(product, file)

    def setup_product_file(self, product, file):
        if not ProductFile.objects.filter(product=product, base_name=file['base_name']).exists():
            product_file = ProductFile.objects.create(product=product, name=file['name'], base_name=file['base_name'])
            with TemporaryFile() as tf:
                try:
                    tf.write(request.urlopen(file['file']).read())
                    tf.seek(0)
                    product_file.file.save(self._make_new_name(file['file']), File(tf))
                except request.HTTPError:
                    product_file.delete()
                except request.URLError:
                    product_file.delete()

    def _make_new_name(self, name):
        orig_name, extension = os.path.splitext(name)
        random_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(40))
        return random_name + extension

    def get_material(self, material: str) -> str:
        return self.materials[material] if material in self.materials else material

    def get_sex(self, sex):
        return self.sex[sex] if sex in self.sex else sex

    def get_prints(self, print_):
        return self.prints[print_] if print_ in self.prints else print_

    def _prepare_price(self, price: float, base_product) -> Tuple[float, float]:
        if base_product.brand and base_product.brand.coefficient:
            coefficient = base_product.brand.coefficient
        else:
            coefficient = self.product_importer.coefficient
        percent = coefficient / 100
        price = math.ceil(price)
        if coefficient == 100:
            return 0, price
        if coefficient > 100:
            return 0, math.ceil(price * percent)
        return price, math.ceil(price * percent)

    def _get_categories(self, imported_categories):
        return ImportedCategory.objects.filter(
            sync_id__in=imported_categories, equivalent_category__isnull=False
        ).values_list('equivalent_category', flat=True)

    def _get_colors(self, imported_colors):
        return Color.objects.filter(name__in=imported_colors).values_list('id', flat=True)

    def _get_materials(self, imported_materials):
        return Material.objects.filter(name__in=imported_materials).values_list('id', flat=True)

    def _setup_colors(self, product_data_list):
        for product_data in product_data_list:
            for color in product_data['colors']:
                Color.objects.get_or_create(name=color)

    def _setup_materials(self, product_data_list):
        for product_data in product_data_list:
            for material_data in product_data['materials']:
                Material.objects.get_or_create(name=material_data)

    @property
    def parser_name(self):
        return ''

    @property
    def report_class(self):
        return ''
