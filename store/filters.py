import django_filters
from .models import *


class CustomCharFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field.widget.attrs.update({'class': 'form-control',})


class ProductFilter(django_filters.FilterSet):
    price = django_filters.RangeFilter(
        label='Price range (Enter Only Numbers)',
        widget=django_filters.widgets.RangeWidget(attrs={'class': 'form-control'})
    )

    description = CustomCharFilter(field_name='description', lookup_expr='icontains', label='Description Contains??')

    class Meta:
        model = Product
        fields = ['product_type', 'category', 'price', 'description', ]


class ProductPage(django_filters.FilterSet):
    name = CustomCharFilter(field_name='name', lookup_expr='icontains', label='Name Contains??')

    class Meta:
        model = Product
        fields = ['product_type', 'category', 'name', ]
