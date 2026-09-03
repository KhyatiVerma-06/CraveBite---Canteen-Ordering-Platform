from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from .models import FoodItem

def home(request):
    template = loader.get_template('Home.html')
    return HttpResponse(template.render())

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