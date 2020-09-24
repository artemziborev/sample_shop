from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
    fields = ('order', 'cost', 'status', 'inner_id', 'inner_key', 'created', 'modified')
    readonly_fields = ('order', 'cost', 'status', 'inner_id', 'inner_key', 'created', 'modified')
