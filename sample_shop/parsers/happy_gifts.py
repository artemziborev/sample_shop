import json
from xml.etree import ElementTree as ET

import requests
from requests.models import Response

from sample_shop.parsers.models import HappyGiftsReport
from .base import BaseParser


class SampleParser(BaseParser):
    def _get_products_file_xml(self) -> Response:
        return requests.get('')

    def _dump_products_file_xml(self):
        with open('products.xml', 'wb') as f:
            f.write(self._get_products_file_xml().content)

    def _get_imported_category(self) -> list:
        dom = ET.fromstring(self._get_products_file_xml().text)
        groups = dom.find('Catalog_groups')
        categories = []
        for group in groups:
            id_ = group.find('ID').text
            name = group.find('NAME').text
            if not id_ or not name:
                continue

            sync_id = self.generate_sync_id(id_)
            parent_sync_id = None
            category = {'sync_id': sync_id, 'parent_sync_id': parent_sync_id, 'name': name}
            categories.append(category)

            sub_groups = group.findall('SUB_Group')
            for sub_group in sub_groups:
                sub_group_id = sub_group.find('ID').text

                sub_group_name = sub_group.find('NAME').text
                sub_group_sync_id = self.generate_sync_id(sub_group_id)
                sub_group_category = {'sync_id': sub_group_sync_id, 'parent_sync_id': sync_id, 'name': sub_group_name}
                categories.append(sub_group_category)

                sub_child_group = sub_group.findall('SUB_CHILD_Group')
                for sub_child in sub_child_group:
                    sub_child_id = sub_child.find('ID').text
                    sub_child_name = sub_child.find('NAME').text

                    sub_child_sync_id = self.generate_sync_id(sub_child_id)
                    sub_child_category = {
                        'sync_id': sub_child_sync_id,
                        'parent_sync_id': sub_group_sync_id,
                        'name': sub_child_name,
                    }
                    categories.append(sub_child_category)

                    sub_child_group_2 = sub_child.findall('SUB_CHILD_Group_2')
                    for sub_child_2 in sub_child_group_2:
                        sub_child_id_2 = sub_child_2.find('ID').text
                        sub_child_name_2 = sub_child_2.find('NAME').text

                        sub_child_sync_id_2 = self.generate_sync_id(sub_child_id_2)
                        sub_child_category_2 = {
                            'sync_id': sub_child_sync_id_2,
                            'parent_sync_id': sub_child_sync_id,
                            'name': sub_child_name_2,
                        }
                        categories.append(sub_child_category_2)

        return categories

    def _get_item_colors(self, item):
        colors = []
        color_node = item.find('Color')
        if color_node is not None and color_node.text is not None:
            colors = [color.lower() for color in color_node.text.strip().split(',')]
        return colors

    def _get_imported_products(self):
        dom = ET.fromstring(self._get_products_file_xml().text)
        # dom = ET.parse('hg_products.xml')
        items = dom.find('Items')
        products = []
        for item in items:  # [:32]
            sex_list = list(
                map(
                    lambda x: self.get_sex(x.strip().lower()),
                    filter(bool, [sub_item.find('GENDER').text for sub_item in item.find('SubItems')]),
                )
            )
            prints = item.find('Applications').text
            is_sublimation = False
            if prints is not None:
                is_sublimation = 'сублимация' in prints.strip().lower().split(';')

            materials = []
            material_list = item.find('MATERIALS').text
            if material_list:
                materials = list(
                    set(
                        map(
                            lambda x: self.get_material(x.lower().strip()),
                            filter(bool, material_list.strip().split(';')),
                        )
                    )
                )
            category_id = item.find('GROUP_ID').text.strip()
            product_data = {
                'name': item.find('NAME').text.strip(),
                'article': item.find('Article').text.strip(),
                'remote_id': self.generate_sync_id(item.find('ID').text.strip()),
                'brand': item.find('BrendName').text.strip(),
                'categories': [self.generate_sync_id(category_id)],
                'colors': self._get_item_colors(item),
                'sex': sex_list[0] if len(sex_list) else '',
                'is_sublimation': is_sublimation,
                'materials': materials,
                'attributes': json.dumps(
                    {
                        'Объем': '{} м3.'.format(item.find('UnitVolume').text.strip()),
                        'Вес': '{} кг.'.format(item.find('UnitWeight').text.strip()),
                    }
                ),
                'is_new': True in list(map(bool, [sub_item.find('New').text for sub_item in item.find('SubItems')])),
                'sub_product_data_list': [],
            }
            group_id_list = []
            for sub_item in item.find('SubItems'):
                full_article = sub_item.find('FullArticle').text.strip()
                article = '/'.join(full_article.split(' '))
                if '.' in full_article:
                    group_id = '{}-{}'.format(category_id, full_article.split(' ')[0])
                else:
                    group_id = '{}-{}'.format(category_id, article)
                main = False
                if group_id not in group_id_list:
                    main = True
                    group_id_list.append(group_id)

                content = ''
                comment = sub_item.find('Comment').text
                if comment is not None:
                    content = comment.strip()

                size = ''
                clothes_size_node = sub_item.find('ClothesSize')
                size_node = sub_item.find('Size')
                if (
                    clothes_size_node is not None
                    and clothes_size_node.text is not None
                    and clothes_size_node.text.strip() != ''
                ):
                    size = clothes_size_node.text.strip().lower()
                elif size_node is not None and size_node.text is not None and size_node.text.strip() != '':
                    size = size_node.text.strip().lower()

                xml_id = sub_item.find('XML_ID').text.strip()
                pdf = '{}.pdf'.format(xml_id)
                cdr = '{}.cdr'.format(xml_id)
                pdf_url = 'https://happygifts.ru/catalog_files/{}'.format(pdf)
                cdr_url = 'https://happygifts.ru/catalog_files/{}'.format(cdr)
                file_list = [
                    {'name': 'Конструктор PDF', 'base_name': pdf, 'file': pdf_url},
                    {'name': 'Конструктор CDR', 'base_name': cdr, 'file': cdr_url},
                ]

                sub_product_data = {
                    'name': sub_item.find('NAME').text.strip(),
                    'remote_id': self.generate_sync_id(sub_item.find('ID').text.strip()),
                    'price': float(sub_item.find('Price').text.strip()),
                    'article': article,
                    'group_id': group_id,
                    'main': main,
                    'content': content,
                    'stock': int(sub_item.find('FreeQuantityCenter').text.strip()),
                    'size': size,
                    'images': [image.text.strip() for image in sub_item.findall('Image')],
                    'file_list': file_list,
                    'colors': self._get_item_colors(sub_item),
                }
                product_data['sub_product_data_list'].append(sub_product_data)
                print(product_data)
            products.append(product_data)
        return products

    @property
    def parser_name(self):
        return 'happy_gifts'

    @property
    def report_class(self):
        return HappyGiftsReport
