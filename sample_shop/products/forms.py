import json

from django import forms
from django.db.models import Q
# from django.db.models.expressions import RawSQL

from .models import BaseProduct, SubProduct, Image, Color, Brand, Material


class ParsedBaseProductForm(forms.ModelForm):
    class Meta:
        model = BaseProduct
        fields = (
            'name',
            'categories',
            'article',
            'remote_id',
            'brand',
            'colors',
            'sex',
            'is_sublimation',
            'materials',
            'attributes',
            'is_new',
            'importer',
        )


class ParsedSubProductForm(forms.ModelForm):
    class Meta:
        model = SubProduct
        fields = (
            'base_product',
            'name',
            'remote_id',
            'old_price',
            'price',
            'article',
            'group_id',
            'main',
            'content',
            'stock',
            'size',
            'colors',
        )


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('product', 'remote_url', 'main_image')


class BaseFilterForm(forms.Form):
    sort = forms.ChoiceField(
        required=False,
        choices=(
            # (BaseProduct.DEFAULT_SORT, 'Популярность'),
            ('price', 'Цена по возрастанию'),
            ('-price', 'Цена по убыванию'),
            # ('-is_new', 'По новинкам'),
        ),
        widget=forms.Select(attrs={'class': 'selectmenu'}),
        initial=BaseProduct.DEFAULT_SORT, label='Цена'
    )
    # circulation = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Тираж', 'min': 0}))
    # price_from = forms.IntegerField(
    #     required=False, widget=forms.NumberInput(attrs={'placeholder': 'Цена от', 'min': 0})
    # )
    # price_to = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Цена до', 'min': 0}))
    brands = forms.MultipleChoiceField(choices=[('-1', 'Без бренда')], required=False, label='Бренд')
    colors = forms.ModelMultipleChoiceField(
        Color.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'js-selectric', 'data-selectric-opt': json.dumps({'first': 'Цвет'})}
        ), label='Цвет'
    )
    # sex = forms.MultipleChoiceField(
    #     required=False,
    #     widget=forms.SelectMultiple(
    #         attrs={'class': 'js-selectric', 'data-selectric-opt': json.dumps({'first': 'Пол'})}
    #     ),
    # )
    # is_sublimation = forms.BooleanField(required=False, label='Cублимация')

    def __init__(self, *args, base_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        brand_queryset = Brand.objects.all()
        if base_queryset:
            brand_queryset = Brand.objects.filter(product_list__in=base_queryset).distinct()
        if brand_queryset.exists():
            self.fields['brands'].choices = self.fields['brands'].choices + [
                (brand.id, brand.name) for brand in brand_queryset
            ]

        color_queryset = Color.objects.all()
        if base_queryset:
            color_queryset = Color.objects.filter(product_list__in=base_queryset).distinct()
        if color_queryset.exists():
            self.fields['colors'].queryset = color_queryset

        product_queryset = BaseProduct.objects.all()
        if base_queryset:
            product_queryset = base_queryset.filter()
        sex_queryset = product_queryset.exclude(sex='').values_list('sex', flat=True).order_by('sex').distinct('sex')
        if sex_queryset.exists():
            self.fields['sex'].choices = [(i, i) for i in sex_queryset]

    def _get_q_brands(self):
        if '-1' in self.cleaned_data['brands']:
            self.cleaned_data['brands'].remove('-1')
            q_brands = Q(brand__in=list(map(int, self.cleaned_data['brands']))) | Q(brand__isnull=True)
        else:
            q_brands = Q(brand__in=list(map(int, self.cleaned_data['brands'])))
        return q_brands

    def _get_q_colors(self):
        return Q(colors__in=self.cleaned_data['colors'])

    # def _get_q_sex(self):
    #     return Q(sex__in=self.cleaned_data['sex'])
    #
    # def _get_q_price_from(self):
    #     return Q(price__gte=self.cleaned_data['price_from'])
    #
    # def _get_q_price_to(self):
    #     return Q(price__lte=self.cleaned_data['price_to'])
    #
    # def _get_q_circulation(self):
    #     return Q(stock__gte=self.cleaned_data['circulation'])

    # def _get_q_is_sublimation(self):
    #     return Q(is_sublimation=self.cleaned_data['is_sublimation'])

    def _get_q_materials(self):
        return Q(attributes__Материал__in=self.cleaned_data['materials'])

    def _get_q(self):
        q_obj = Q()
        if self.cleaned_data['brands']:
            q_obj.add(self._get_q_brands(), Q.AND)
        if self.cleaned_data['colors']:
            q_obj.add(self._get_q_colors(), Q.AND)
        # if self.cleaned_data['sex']:
        #     q_obj.add(self._get_q_sex(), Q.AND)
        # if self.cleaned_data['price_from']:
        #     q_obj.add(self._get_q_price_from(), Q.AND)
        # if self.cleaned_data['price_to']:
        #     q_obj.add(self._get_q_price_to(), Q.AND)
        # if self.cleaned_data['circulation']:
        #     q_obj.add(self._get_q_circulation(), Q.AND)
        # if self.cleaned_data['is_sublimation']:
        #     q_obj.add(self._get_q_is_sublimation(), Q.AND)
        return q_obj

    def filter_queryset(self, queryset):
        return queryset.filter(self._get_q())


class FilterForm(BaseFilterForm):
    materials = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'js-selectric', 'data-selectric-opt': json.dumps({'first': 'Материал'})}
        ),
    )
    is_on_sale = forms.BooleanField(required=False)

    def __init__(self, *args, base_queryset=None, **kwargs):
        super().__init__(*args, base_queryset=base_queryset, **kwargs)

        material_queryset = Material.objects.all()
        if base_queryset:
            material_queryset = Material.objects.filter(product_list__in=base_queryset).distinct()
        if material_queryset.exists():
            self.fields['materials'].choices = [(material.id, material.name) for material in material_queryset]

    def _get_q(self):
        q_obj = super()._get_q()
        if self.cleaned_data['materials']:
            q_obj.add(self._get_q_materials(), Q.AND)
        return q_obj


# class SmallFilterForm(BaseFilterForm):
#     search = forms.CharField(min_length=3, widget=forms.HiddenInput, required=False)

class AdminUpdatePriceForm(forms.Form):
    products = forms.ModelMultipleChoiceField(queryset=BaseProduct.objects.all(), widget=forms.MultipleHiddenInput)
    old_price = forms.DecimalField(label='Старая цена', required=True, widget=forms.NumberInput)
    discount_coeff = forms.IntegerField(label='Скидка', required=True, widget=forms.NumberInput)

    def update_prices(self):
        for product in self.cleaned_data['products']:
            if self.cleaned_data['old_price']:
                product.old_price = self.cleaned_data['old_price']
            if self.cleaned_data['discount_coeff']:
                product.discount_coeff = self.cleaned_data['discount_coeff']
            product.save()


class ProductUploadForm(forms.Form):
    file_to_upload = forms.FileField(label='Файл в формате CSV')
