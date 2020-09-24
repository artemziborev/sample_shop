from django import forms

from .models import ImportedCategory


class ImportedCategoryForm(forms.ModelForm):
    class Meta:
        model = ImportedCategory
        fields = ('name', 'parent', 'sync_id')
