from django import forms
from .models import *


# forms.py
class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search for Product Names and Descriptions',
            'class': 'form-control',
        }),
        label='',  # Set label to an empty string to remove it
    )


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = '__all__'

    def clean(self):
        super(ProductTypeForm, self).clean()
        name = self.cleaned_data.get('name')

        # Double Value Validation
        for instance in ProductType.objects.all():
            if instance.name == name:
                raise forms.ValidationError(f'{name} already exist')
        return self.cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def clean(self):
        super(CategoryForm, self).clean()
        name = self.cleaned_data.get('name')

        # Double Value Validation
        for instance in Category.objects.all():
            if instance.name == name:
                raise forms.ValidationError(f'{name} already exist')
        return self.cleaned_data


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    # Apply common CSS class to all fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control form-control-md'
            else:
                field.widget.attrs['class'] = 'form-control form-control-md'

    def clean(self):
        super(AddProductForm, self).clean()
        name = self.cleaned_data.get('name')

        # Double Value Validation
        for instance in Product.objects.all():
            if instance.name == name:
                raise forms.ValidationError(f'{name} already exist')
        return self.cleaned_data


class UpdateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    # Apply common CSS class to all fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control form-control-md'
            else:
                field.widget.attrs['class'] = 'form-control form-control-md'
