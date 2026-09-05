from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from .models import FoodItem, Order, OrderItem

def home(request):
    search_query = request.GET.get('q', '').strip()

    if search_query:
        search_results = FoodItem.objects.filter(
            name__icontains=search_query
        ) | FoodItem.objects.filter(
            category__icontains=search_query
        ) | FoodItem.objects.filter(
            description__icontains=search_query
        )
    else:
        search_results = FoodItem.objects.none()

    return render(request, 'Home.html', {
        'search_query': search_query,
        'search_results': search_results
    })

def menu(request):
    food_items = FoodItem.objects.all()

    return render(request, 'Menu.html', {
        'food_items': food_items
    })
def add_to_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] += 1
    else:
        cart[food_id] = 1

    request.session['cart'] = cart

    return redirect('menu')
def cart(request):
    cart_data = request.session.get('cart', {})

    cart_items = []
    total = 0

    for food_id, quantity in cart_data.items():
        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity
        total += item_total

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'item_total': item_total
        })

    return render(request, 'Cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def checkout(request):
    cart_data = request.session.get('cart', {})

    cart_items = []
    total = 0

    for food_id, quantity in cart_data.items():
        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity
        total += item_total

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'item_total': item_total
        })

    return render(request, 'Checkout.html', {
        'cart_items': cart_items,
        'total': total
    })    


def increase_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] += 1

    request.session['cart'] = cart

    return redirect('cart')
def decrease_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] -= 1

        if cart[food_id] <= 0:
            del cart[food_id]

    request.session['cart'] = cart

    return redirect('cart')

def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart

    return redirect('cart')

def offers(request):
    template = loader.get_template('Offers.html')
    return HttpResponse(template.render())

def about(request):
    template = loader.get_template('About.html')
    return HttpResponse(template.render())

def login(request):
    template = loader.get_template('Login.html')
    return HttpResponse(template.render())

def signup(request):
    template = loader.get_template('Signup.html')
    return HttpResponse(template.render())

def place_order(request):
    if request.method == 'POST':

        cart_data = request.session.get('cart', {})

        if not cart_data:
            return redirect('cart')

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        total = 0

        for food_id, quantity in cart_data.items():
            food = FoodItem.objects.get(id=food_id)
            total += food.price * quantity

        order = Order.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            payment_method=payment_method,
            total_amount=total
        )

        for food_id, quantity in cart_data.items():
            food = FoodItem.objects.get(id=food_id)

            OrderItem.objects.create(
                order=order,
                food=food,
                quantity=quantity,
                price=food.price
            )

        request.session['cart'] = {}

        return redirect('order_success', order_id=order.id)

    return redirect('checkout')

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)

    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'OrderSuccess.html', {
        'order': order,
        'order_items': order_items
    })

def my_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    return render(request, 'MyOrders.html', {
        'orders': orders
    })