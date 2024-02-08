import django_filters
from .models import *


class CustomCharFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field.widget.attrs.update({'class': 'form-control', 'placeholder': 'Description Contains...??'})


class ProductFilter(django_filters.FilterSet):
    price = django_filters.RangeFilter(
        label='Price range (Enter Only Numbers)',
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'form-control'})
    )

    description = CustomCharFilter(field_name='description', lookup_expr='icontains', label='Description filter')

    class Meta:
        model = Product
        fields = ['product_type', 'category', 'price', 'description',]
