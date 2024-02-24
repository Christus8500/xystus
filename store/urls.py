from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('cart/', views.cart, name='cart'),
    path('shop/', views.shop, name='shop'),
    path('order/', views.order, name='order'),
    path('contact/', views.contact, name='contact'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('update_item/', views.update_item, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),
    path('product_detail/<str:product_id>/', views.productDetail, name='product_detail'),
    path('product_type/<str:pk>/', views.product_type_detail, name='product_type_detail'),
]
