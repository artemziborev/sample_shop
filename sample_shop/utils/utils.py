import random
from slugify import slugify
import os
from django.db.models import Sum

from sample_shop.catalog import models as catalog_models
from sample_shop.products import models as products_models


def get_unique_slug_for_model(name, class_):
    slug = slugify(name)
    while class_.objects.filter(slug=slug).exists():
        slug = '-'.join([slugify(name), str(random.randint(1, 1000))])
    return slug

def clear_product_file():
    for product in products_models.SubProduct.objects.all():
        for file in product.files.all():
            if not os.path.exists(file.file.path):
                file.delete()

def update_category(category):
    category.product_count = category.get_product_count()
    # category.url = category.get_path()
    if category.slug == 'rasprodazha':
        category.product_count = (
            products_models.BaseProduct.objects.annotate(full_stock=Sum('sub_product_list__stock'))
            .filter(full_stock__gt=1)
            .filter(is_hidden=False)
            .filter(sub_product_list__old_price__gt=0)
            .distinct()
            .count()
        )
    # category.save(update_fields=('product_count', 'url'))
    category.save()


def update_categories():
    for c in catalog_models.Category.objects.all():
        update_category(c)
