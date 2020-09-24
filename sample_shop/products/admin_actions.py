import csv

from django.http import HttpResponse
from django.shortcuts import redirect


def download_product_list(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=product_list.csv'

    first_row = [
        'наименование',
        'стоимость',
        'распродажа',
        'популярное',
        'новинка',
        'пол',
        'поставщик',
        'остаток',
        'удалённый склад',
        'артикул',
        'бренд',
        'коллекция',
        'цвет',
        'размер',
    ]

    writer = csv.writer(response)
    writer.writerow(first_row)
    for obj in queryset:
        writer.writerow(
            [
                obj.name,
                obj.price,
                'Да' if obj.is_on_sale else 'Нет',
                'Да' if obj.is_popular else 'Нет',
                'Да' if obj.is_new else 'Нет',
                obj.get_sex_display(),
                obj.supplier_info.supplier.name if obj.supplier_info.supplier else 'Нет',
                obj.supplier_info.stock,
                obj.supplier_info.storage,
                obj.article,
                obj.supplier_info.brand.name if obj.supplier_info.brand else 'Нет',
                obj.supplier_info.collection.name if obj.supplier_info.collection else 'Нет',
                ', '.join(obj.color_list.all().values_list('name', flat=True)),
                obj.supplier_info.new_size.size if obj.supplier_info.new_size else 'Нет',
            ]
        )

    return response


download_product_list.short_description = 'Скачать товары'


def download_product_list_for_parser(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=product_list.csv'

    first_row = [
        # при замене наименований столбцов, поправить загрузку товаров upload_products_view
        'наименование',
        'артикул',
        'стоимость',
        'старая цена',
        'скидка в акции',
        'активность'
    ]

    writer = csv.writer(response, delimiter=';')
    writer.writerow(first_row)
    for obj in queryset:
        writer.writerow(
            [
                obj.name,
                obj.article,
                obj.price,
                obj.old_price,
                obj.discount,
                obj.is_active
            ]
        )

    return response


download_product_list_for_parser.short_description = 'Скачать товары для парсера'

def move_product_list(modeladmin, request, queryset):
    request.session['_old_post'] = [i.id for i in queryset]
    return redirect('admin:shop_catalog_product_move')


move_product_list.short_description = 'Редактировать выбранные товары'

def update_product_price(modeladmin, request, queryset):
    request.session['_old_post'] = [i.id for i in queryset]
    return redirect('admin:shop_catalog_update_price')

update_product_price.short_description = 'Изменить цены товаров'
