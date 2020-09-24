import logging

from celery import shared_task
from django.utils import timezone

from sample_shop.orders.models import ProductOrder

logger = logging.getLogger(__name__)


# deprecated
@shared_task
def check_yandex_payment_status():
    logger.info('check_yandex_payment_status')

    orders = ProductOrder.objects.filter(
        payment_type=ProductOrder.PAYMENT_TYPE_ONLINE, status=ProductOrder.STATUS_UNPROCESSED, payment__isnull=False
    )
    for order in orders:
        logger.info(f'order - {order.__dict__}')

        payment = order.payment
        logger.info(f'order.payment - {payment.__dict__}')
        yandex_payment = payment.get_yandex_payment()
        logger.info(f'yandex_payment - {payment.__dict__}')
        payment.status = yandex_payment.status
        payment.save()

        if payment.status == 'succeeded':
            logger.info('payment.status == succeeded:')
            order.online_payment_id = payment.inner_id
            order.online_payment_confirm_date = timezone.now()
            order.status = ProductOrder.STATUS_PAID
            order.confirm_online_payment()
            order.confirmed = True
            order.save()

    return {'status': True}
