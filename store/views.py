from django.http import JsonResponse
import json
import datetime
from django.shortcuts import render
from django.conf import settings
from .models import *
from .forms import SearchForm
from .utils import cookieCart, cartData, guestOrder
from .filters import ProductFilter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Create your views here.
def index(request):
    data = cartData(request)
    cartItems = data['cartItems']

    product_types = ProductType.objects.all()[:6]

    products = Product.objects.all()
    product_page = Paginator(products, 16)
    page_number = request.GET.get('page')

    try:
        product_page = product_page.get_page(page_number)
    except PageNotAnInteger:
        product_page = product_page.page(1)
    except EmptyPage:
        product_page = product_page.page(product_page.num_pages)

    cheapest = Product.objects.order_by('price')[:10]
    latest_products = Product.objects.all().order_by('-added_at')[:12]

    # Check if the alert has been shown in the current session
    show_alert = not request.session.get('alert_shown', False)

    # Set the session variable to indicate that the alert has been shown for this session
    if show_alert:
        request.session['alert_shown'] = True

    context = {
        'product_page': product_page,  # Include paginated products
        'product_types': product_types,
        'cheapest': cheapest,
        'latest_products': latest_products,
        'cartItems': cartItems,
        'show_alert': show_alert,
    }
    return render(request, 'store/index.html', context)


def clear_alert_session(request):
    # Clear the session variable
    request.session.pop('alert_shown', None)
    return JsonResponse({'status': 'success'})


def categories(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    my_filter = ProductFilter(request.GET, queryset=products)
    products = my_filter.qs

    context = {
        'cartItems': cartItems,
        'products': products,
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

    context = {
        'cartItems': cartItems,
        'products': products,
        'results': results,
        'form': form,
    }
    return render(request, 'store/shop.html', context)


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