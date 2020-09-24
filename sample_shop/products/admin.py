from django.conf.urls import url
from django.contrib import admin
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

from . import models, forms, admin_actions


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Size)
class SizeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Print)
class PrintAdmin(admin.ModelAdmin):
    pass

class ProductImageInline(admin.TabularInline):
    model = models.Image
    extra = 0

@admin.register(models.SubProduct)
class SubProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    actions = (admin_actions.download_product_list, admin_actions.move_product_list, admin_actions.update_product_price,
               admin_actions.download_product_list_for_parser)

    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns_dop = [url(r'^move/$', self.move_view, name='shop_catalog_product_move'),
                           url(r'^update_price/$', self.update_price_view, name='shop_catalog_update_price'),
                           url(r'^upload_products/$', self.upload_products_view, name='shop_catalog_upload_roducts'),]

        return urlpatterns_dop + urlpatterns
    def save_model(self, request, obj, form, change):
        old_obj = self.get_object(request, obj.id)
        if old_obj and not obj.disable_update_main_image and old_obj.main_image.name != obj.main_image.name:
            obj.disable_update_main_image = True
        super().save_model(request, obj, form, change)

    def move_view(self, request):

        p1 = models.Product.objects.filter(id__in=request.session['_old_post'])

        p2 = models.Product.objects.filter(
            Q(id__in=p1.values_list('color_variant_of', flat=True))
            | Q(id__in=p1.values_list('size_variant_of', flat=True))
        )

        p3 = models.Product.objects.filter(
            Q(color_variant_of__in=p1.values_list('id', flat=True))
            | Q(size_variant_of__in=p1.values_list('id', flat=True))
        )

        product_list = p1 | p2 | p3

        form = forms.CategoryMoveForm(
            initial={
                'products': models.Product.objects.filter(id__in=request.session['_old_post']).values_list(
                    'id', flat=True
                )
            }
        )
        if request.method == 'POST':
            form = forms.CategoryMoveForm(request.POST)
            if form.is_valid():
                form.update_products()
                return redirect('..')
        context = dict(
            self.admin_site.each_context(request),
            title='Выбранные товары',
            product_list=product_list,
            form=form,
            media=self.media,
        )
        return render(request, 'admin/shop_catalog/product_move.html', context)

    def update_price_view(self, request):
        p1 = models.Product.objects.filter(id__in=request.session['_old_post'])

        p2 = models.Product.objects.filter(
            Q(id__in=p1.values_list('color_variant_of', flat=True))
            | Q(id__in=p1.values_list('size_variant_of', flat=True))
        )

        p3 = models.Product.objects.filter(
            Q(color_variant_of__in=p1.values_list('id', flat=True))
            | Q(size_variant_of__in=p1.values_list('id', flat=True))
        )

        product_list = p1 | p2 | p3

        form = forms.AdminUpdatePriceForm(
            initial={
                'products': models.Product.objects.filter(id__in=request.session['_old_post']).values_list(
                    'id', flat=True
                )
            }
        )
        if request.method == 'POST':
            form = forms.AdminUpdatePriceForm(request.POST)
            if form.is_valid():
                form.update_prices()
                return redirect('..')
        context = dict(
            self.admin_site.each_context(request),
            title='Выбранные товары',
            product_list=product_list,
            form=form,
            media=self.media,
        )
        return render(request, 'admin/products/product_update_price.html', context)

    def upload_products_view(self, request):
        if request.method == 'POST':
            form = forms.ProductUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['file_to_upload']
                for line in uploaded_file:
                    if line.decode().split(';')[0] == 'наименование':  #пропускаем первую строку файла
                        continue
                    else:
                        line = line.decode().split(';')
                        if len(line) == 6:
                            name = line[0]
                            article = line[1]
                            data = {'price': line[2],
                                    'old_price': line[3],
                                    'discount': line[4],
                                    'is_active': line[5][:-2]} # Удаляем лишние символы в конце строки
                            models.Product.objects.filter(name=name, article=article).update(**data)
                        else:
                            return HttpResponse('Файл поврежден!')
                return redirect('../')
        else:
            form = forms.ProductUploadForm()
        return render(request, 'admin/shop_catalog/products_upload_form.html', {'form':form})


class SubProductStackedInline(admin.StackedInline):
    model = models.SubProduct
    extra = 0


@admin.register(models.BaseProduct)
class BaseProductAdmin(admin.ModelAdmin):
    inlines = [SubProductStackedInline]
