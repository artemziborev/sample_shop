from celery import shared_task
from celery.utils.log import get_task_logger

from sample_shop.utils.utils import clear_product_file
from .models import FullReport
from .happy_gifts import SampleParser

logger = get_task_logger(__name__)

parser_list = [
    SampleParser,
]

@shared_task
def update_catalog():
    logger.info('start update catalog')
    for parser_class in parser_list:
        parser = parser_class()
        parser.setup_imported_category()
    logger.info('end update catalog')

@shared_task
def update_products():
    logger.info('start update product')
    full_report = FullReport.objects.create()
    for parser_class in parser_list:
        parser = parser_class()
        parser.setup_imported_products()
        report = parser.report
        report.parent = full_report
        report.save()
    clear_product_file()
    logger.info('end update products')
