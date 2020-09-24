from sample_shop.catalog.models import Category
from .forms import CallBackRequestForm
from .models import TopMenuItem, CallBackRequest


# def top_menu_items(request):
#     return {'top_menu_items': TopMenuItem.objects.all(),
#             'callback_form': CallBackRequestForm(CallBackRequest.FORM_TYPE_CALLBACK),
#             'contact_us_form': CallBackRequestForm(CallBackRequest.FORM_TYPE_CONTACT_US),
#             'coop_form': CallBackRequestForm(CallBackRequest.FORM_TYPE_COOP),
#             'categories': Category.objects.all()}
