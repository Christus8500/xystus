import random
from django.contrib import messages
from django.http import JsonResponse
import json
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import *
from .forms import *
from .utils import cookieCart, cartData, guestOrder
from .filters import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import user_passes_test


# Create your views here.
def is_admin(user):
    return user.is_authenticated and user.is_staff


def index(request):
    data = cartData(request)
    cartItems = data['cartItems']

    product_types = ProductType.objects.all()[:6]

    products = Product.objects.all()

    # Shuffle the products
    products_list = list(products)
    random.shuffle(products_list)

    product_page = Paginator(products_list, 16)
    page_number = request.GET.get('page')

    try:
        product_page = product_page.get_page(page_number)
    except PageNotAnInteger:
        product_page = product_page.page(1)
    except EmptyPage:
        product_page = product_page.page(product_page.num_pages)

    cheapest = Product.objects.order_by('price')[:10]
    latest_products = Product.objects.all().order_by('-added_at')[:12]

    context = {
        'product_page': product_page,  # Include paginated products
        'product_types': product_types,
        'cheapest': cheapest,
        'latest_products': latest_products,
        'cartItems': cartItems,
    }
    return render(request, 'store/index.html', context)


def product_type_detail(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']

    product_type = get_object_or_404(ProductType, pk=pk)
    products = Product.objects.filter(product_type=product_type)

    context = {
        'product_type': product_type,
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'store/product_type_detail.html', context)


def categories(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    my_filter = ProductFilter(request.GET, queryset=products)
    products = my_filter.qs

    # Convert the queryset to a list and shuffle it
    products_list = list(products)
    random.shuffle(products_list)

    context = {
        'cartItems': cartItems,
        'products': products_list,  # Use the shuffled list
        'my_filter': my_filter,
    }
    return render(request, 'store/categories.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
    paystack_secret_key = settings.PAYSTACK_SECRET_KEY

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'paystack_public_key': paystack_public_key,
        'paystack_secret_key': paystack_secret_key,
    }
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('ProductId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def clear_cart(request):
    customer = request.user.customer
    cart_items = Order.objects.get(customer=customer, complete=False)
    cart_items.orderitem_set.all().delete()

    return JsonResponse('Cart was cleared', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Error decoding JSON: {e}'}, status=400)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            phone=data['shipping']['phone'],
            email=data['shipping']['email'],
            address=data['shipping']['address'],
            town=data['shipping']['town'],
            lga=data['shipping']['lga'],
            state=data['shipping']['state'],
        )

    return JsonResponse('Payment Complete', safe=False)


def shop(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            results = Product.objects.filter(name__icontains=query) | Product.objects.filter(
                description__icontains=query)
    else:
        form = SearchForm()

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    # Convert the queryset to a list and shuffle it
    products_list = list(products)
    random.shuffle(products_list)

    context = {
        'cartItems': cartItems,
        'products': products_list,
        'results': results,
        'form': form,
    }
    return render(request, 'store/shop.html', context)


def productDetail(request, product_id):
    product_detail = Product.objects.get(id=product_id)
    quick_products = Product.objects.all()[:8]

    explore_products = Product.objects.filter(product_type=product_detail.product_type).exclude(id=product_detail.id)[
                       :12]
    # Convert the queryset to a list and shuffle it
    products_list = list(explore_products)
    random.shuffle(products_list)

    data = cartData(request)
    cartItems = data['cartItems']
    context = {
        'cartItems': cartItems,
        'product_detail': product_detail,
        'quick_products': quick_products,
        'explore_products': products_list,
    }
    return render(request, 'store/product_detail.html', context)


@user_passes_test(is_admin)
def order(request):
    data = cartData(request)
    cartItems = data['cartItems']

    orders = Order.objects.all().order_by('-date_ordered')

    context = {
        'cartItems': cartItems,
        'orders': orders,
    }
    return render(request, 'store/orders.html', context)


def contact(request):
    data = cartData(request)
    cartItems = data['cartItems']

    context = {
        'cartItems': cartItems,
    }
    return render(request, 'store/contact.html', context)


@user_passes_test(is_admin)
def product(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    my_filter = ProductPage(request.GET, queryset=products)
    products = my_filter.qs

    context = {
        'cartItems': cartItems,
        'products': products,
        'my_filter': my_filter,
    }
    return render(request, 'store/product.html', context)


@user_passes_test(is_admin)
def addProduct(request):
    form = AddProductForm()
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('product')  # Update 'home' to your home page URL name
        else:
            messages.error(request, 'Form submission failed. Please check the data.')

    context = {
        'form': form,
    }
    return render(request, 'store/add_product.html', context)


@user_passes_test(is_admin)
def updateProduct(request, product_id):
    products = get_object_or_404(Product, id=product_id)
    form = UpdateProductForm(instance=products)

    if request.method == "POST":
        form = UpdateProductForm(request.POST, request.FILES, instance=products)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product')
        else:
            messages.error(request, 'Form submission failed. Please check the data.')

    context = {
        'form': form,
        'products': products,
    }
    return render(request, 'store/update_product.html', context)


@user_passes_test(is_admin)
def addCategory(request):
    form = CategoryForm
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Category Added successfully.')
            return redirect('product')
        else:
            messages.error(request, 'Form submission failed. Please check the data.')

    category = Category.objects.all()

    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'store/add_category.html', context)


@user_passes_test(is_admin)
def addProductType(request):
    form = ProductTypeForm
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Product Type Added successfully.')
            return redirect('product')
        else:
            messages.error(request, 'Form submission failed. Please check the data.')

    product_types = ProductType.objects.all()

    context = {
        'form': form,
        'product_types': product_types,
    }
    return render(request, 'store/add_product_type.html', context)
