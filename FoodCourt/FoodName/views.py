from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg, Count, Prefetch, Sum
from django.db.models.functions import TruncDate
from .models import FoodItem, Order, OrderItem, FoodReview, Coupon, DeliveryPartner, OrderNotification
from django.utils import timezone
from decimal import Decimal

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

    is_delivery_partner = False

    if request.user.is_authenticated:
        is_delivery_partner = DeliveryPartner.objects.filter(
            user=request.user
        ).exists()

    return render(request, 'Home.html', {
        'search_query': search_query,
        'search_results': search_results,
        'is_delivery_partner': is_delivery_partner
    })

def menu(request):
    food_items = FoodItem.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    cart_data = request.session.get('cart', {})

    for food in food_items:
        food.cart_quantity = cart_data.get(str(food.id), 0)

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
    request.session.modified = True

    return redirect('menu')

def cart(request):

    cart_data = request.session.get('cart', {})

    cart_items = []
    subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'item_total': item_total,
        })

        subtotal += item_total

    # Coupon / Offer details
    coupon_code = request.session.get('coupon_code')
    offer_code = request.session.get('offer_code')

    discount = Decimal('0.00')
    final_total = subtotal

    # --------------------------------------------------
    # PIZZA20 / BURGER15 OFFER
    # --------------------------------------------------

    active_offer = offer_code or coupon_code

    if active_offer in ['PIZZA20', 'BURGER15']:

        try:
            offer = Coupon.objects.get(
                code=active_offer,
                is_active=True
            )

            if offer.expiry_date >= timezone.now():

                eligible_amount = Decimal('0.00')

                for food_id, quantity in cart_data.items():

                    food = FoodItem.objects.get(id=food_id)

                    item_total = food.price * quantity

                    if (
                        active_offer == 'PIZZA20'
                        and food.category.strip().lower() == 'pizza'
                    ):
                        eligible_amount += item_total

                    elif (
                        active_offer == 'BURGER15'
                        and food.category.strip().lower() == 'burger'
                    ):
                        eligible_amount += item_total

                if eligible_amount > 0:

                    discount = (
                        eligible_amount
                        * Decimal(offer.discount_percent)
                        / Decimal('100')
                    )

                    final_total = subtotal - discount

                    request.session['coupon_code'] = offer.code
                    request.session['coupon_discount'] = str(discount)
                    request.session['final_total'] = str(final_total)

                    request.session.modified = True

                    coupon_code = offer.code

                else:

                    request.session.pop('coupon_code', None)
                    request.session.pop('coupon_discount', None)
                    request.session.pop('final_total', None)

                    coupon_code = None
                    discount = Decimal('0.00')
                    final_total = subtotal

                    messages.info(
                        request,
                        'Add an eligible item to use this offer.'
                    )

            else:

                request.session.pop('offer_code', None)
                request.session.pop('coupon_code', None)
                request.session.pop('coupon_discount', None)
                request.session.pop('final_total', None)

                coupon_code = None

        except Coupon.DoesNotExist:

            request.session.pop('offer_code', None)
            request.session.pop('coupon_code', None)
            request.session.pop('coupon_discount', None)
            request.session.pop('final_total', None)

            coupon_code = None

    # --------------------------------------------------
    # NORMAL COUPON
    # --------------------------------------------------

    elif coupon_code:

        try:

            coupon = Coupon.objects.get(
                code=coupon_code,
                is_active=True
            )

            if (
                coupon.expiry_date >= timezone.now()
                and subtotal >= coupon.minimum_order_amount
            ):

                discount = (
                    subtotal
                    * Decimal(coupon.discount_percent)
                    / Decimal('100')
                )

                final_total = subtotal - discount

            else:

                request.session.pop('coupon_code', None)
                request.session.pop('coupon_discount', None)
                request.session.pop('final_total', None)

                coupon_code = None
                discount = Decimal('0.00')
                final_total = subtotal

        except Coupon.DoesNotExist:

            request.session.pop('coupon_code', None)
            request.session.pop('coupon_discount', None)
            request.session.pop('final_total', None)

            coupon_code = None
            discount = Decimal('0.00')
            final_total = subtotal

    # Safety check
    if final_total < 0:
        final_total = Decimal('0.00')

    return render(request, 'Cart.html', {
        'cart_items': cart_items,
        'total': subtotal,
        'subtotal': subtotal,
        'discount': discount,
        'final_total': final_total,
        'coupon_code': coupon_code,
    })

def checkout(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart_data = request.session.get('cart', {})

    cart_items = []
    subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity
        subtotal += item_total

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'item_total': item_total
        })

    # Get coupon discount from session
    discount = Decimal(
        str(request.session.get('coupon_discount', '0'))
    )

    final_total = subtotal - discount

    # Safety check
    if final_total < 0:
        final_total = Decimal('0.00')

    return render(request, 'Checkout.html', {
        'cart_items': cart_items,
        'total': final_total,
        'subtotal': subtotal,
        'discount': discount,
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


def menu_increase_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] += 1
    else:
        cart[food_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('menu')

def menu_decrease_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id] -= 1

        if cart[food_id] <= 0:
            del cart[food_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('menu')

def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})

    food_id = str(food_id)

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart

    return redirect('cart')

def offers(request):
    return render(request, 'Offers.html')

def about(request):
    return render(request, 'About.html')

def login(request):

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        users = User.objects.filter(email=email)

        user = None

        for user_obj in users:
            authenticated_user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if authenticated_user is not None:
                user = authenticated_user
                break

        if user is not None:

            auth_login(request, user)

            messages.success(
                request,
                f'Welcome, {user.first_name}! You are logged in successfully.'
            )

            # Delivery Partner → Delivery Dashboard
            if DeliveryPartner.objects.filter(user=user).exists():
                return redirect('delivery_dashboard')

            return redirect('home')

        messages.error(
            request,
            'Invalid email or password.'
        )
        return redirect('login')

    return render(request, 'Login.html')

def signup(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return redirect('signup')

        # Full name ko first name aur last name mein divide karna
        name_parts = name.split(' ', 1)

        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(
            request,
            'Account created successfully. Please login.'
        )

        return redirect('login')

    return render(request, 'Signup.html')

def place_order(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart_data = request.session.get('cart', {})
    checkout_details = request.session.get('checkout_details', {})

    if not cart_data:
        return redirect('cart')

    # Get checkout details from session
    name = checkout_details.get('name', '')
    phone = checkout_details.get('phone', '')
    email = checkout_details.get('email', '')
    address = checkout_details.get('address', '')
    payment_method = checkout_details.get(
        'payment_method',
        'Cash on Delivery'
    )

    # Calculate subtotal
    subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():
        food = FoodItem.objects.get(id=food_id)
        subtotal += food.price * quantity

    # Get coupon discount
    discount = Decimal(
        str(request.session.get('coupon_discount', '0'))
    )

    total = subtotal - discount

    if total < 0:
        total = Decimal('0.00')

    # Create order
    order = Order.objects.create(
        user=request.user,
        name=name,
        phone=phone,
        email=email,
        address=address,
        payment_method=payment_method,
        total_amount=total
    )

    # Create order items
    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        OrderItem.objects.create(
            order=order,
            food=food,
            quantity=quantity,
            price=food.price
        )

    # Clear cart
    request.session['cart'] = {}

    # Clear checkout details
    request.session['checkout_details'] = {}

    # Clear coupon
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    request.session.pop('final_total', None)
    request.session.pop('offer_code', None)

    request.session.modified = True

    return redirect('order_success', order_id=order.id)   

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)

    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'OrderSuccess.html', {
        'order': order,
        'order_items': order_items
    })

def my_orders(request):

    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'MyOrders.html', {
        'orders': orders
    })

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    is_delivery_partner = DeliveryPartner.objects.filter(
        user=request.user
    ).exists()

    return render(request, 'Profile.html', {
        'is_delivery_partner': is_delivery_partner
    })

def settings(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':

        # Personal information update
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.username = email
        request.user.save()

        messages.success(
            request,
            'Your account details have been updated successfully.'
        )

        return redirect('settings')

    return render(request, 'Settings.html')

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Current password check
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('settings')

        # New passwords match check
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('settings')

        # Password update
        request.user.set_password(new_password)
        request.user.save()

        messages.success(
            request,
            'Password changed successfully. Please login again.'
        )

        logout(request)
        return redirect('login')

    return redirect('settings')


def save_checkout_details(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        request.session['checkout_details'] = {
            'name': request.POST.get('name', ''),
            'phone': request.POST.get('phone', ''),
            'email': request.POST.get('email', ''),
            'address': request.POST.get('address', ''),
            'payment_method': request.POST.get('payment_method', '')
        }

        request.session.modified = True

        payment_method = request.POST.get('payment_method')

        if payment_method == 'UPI':
            return redirect('/demo-payment/?app=UPI')

        if payment_method == 'Credit / Debit Card':
            return redirect('/demo-payment/?app=Card')

        return redirect('place_order')

    return redirect('checkout')

def demo_payment(request):

    app_name = request.GET.get('app', 'UPI')

    cart_data = request.session.get('cart', {})

    if not cart_data:
        return redirect('cart')

    cart_items = []
    subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity

        subtotal += item_total

        cart_items.append({
            'food': food,
            'quantity': quantity,
            'item_total': item_total
        })

    # Get coupon discount
    discount = Decimal(
        str(request.session.get('coupon_discount', '0'))
    )

    final_total = subtotal - discount

    if final_total < 0:
        final_total = Decimal('0.00')

    checkout_details = request.session.get(
        'checkout_details',
        {}
    )

    return render(request, 'DemoPayment.html', {
        'app_name': app_name,
        'cart_items': cart_items,
        'total': final_total,
        'subtotal': subtotal,
        'discount': discount,
        'checkout_details': checkout_details
    })

def demo_payment_success(request):

    if not request.user.is_authenticated:
        return redirect('login')

    cart_data = request.session.get('cart', {})
    checkout_details = request.session.get(
        'checkout_details',
        {}
    )

    if not cart_data:
        return redirect('cart')

    # Calculate subtotal
    subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        subtotal += food.price * quantity

    # Get coupon discount
    discount = Decimal(
        str(request.session.get('coupon_discount', '0'))
    )

    total = subtotal - discount

    if total < 0:
        total = Decimal('0.00')

    # Create order
    order = Order.objects.create(
        user=request.user,
        name=checkout_details.get('name', ''),
        phone=checkout_details.get('phone', ''),
        email=checkout_details.get('email', ''),
        address=checkout_details.get('address', ''),
        payment_method=checkout_details.get(
            'payment_method',
            'UPI - Demo Payment'
        ),
        total_amount=total
    )

    # Create order items
    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        OrderItem.objects.create(
            order=order,
            food=food,
            quantity=quantity,
            price=food.price
        )

    # Clear cart
    request.session['cart'] = {}

    # Clear checkout details
    request.session['checkout_details'] = {}

    # Clear coupon
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    request.session.pop('final_total', None)

    # Clear selected offer
    request.session.pop('offer_code', None)

    request.session.modified = True

    return render(request, 'DemoPaymentSuccess.html', {
        'order': order
    })

def add_review(request, food_id):
    if not request.user.is_authenticated:
        return redirect('login')

    food = FoodItem.objects.get(id=food_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review', '').strip()

        if rating:
            FoodReview.objects.create(
                user=request.user,
                food=food,
                rating=int(rating),
                review=review
            )

        return redirect('menu')

    return render(request, 'Review.html', {
        'food': food
    })

def reviews(request):

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect('login')

        food_id = request.POST.get('food')
        rating = request.POST.get('rating')
        review_text = request.POST.get('review', '').strip()

        if food_id and rating:
            food = FoodItem.objects.get(id=food_id)

            FoodReview.objects.create(
                user=request.user,
                food=food,
                rating=int(rating),
                review=review_text
            )

        return redirect('reviews')

    food_items = FoodItem.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).prefetch_related(
        Prefetch(
            'reviews',
            queryset=FoodReview.objects.select_related('user').order_by('-created_at')
        )
    ).order_by(
        'category',
        'name'
    )

    return render(request, 'Reviews.html', {
        'food_items': food_items,
    })

def apply_coupon(request):

    if request.method != 'POST':
        return redirect('cart')

    coupon_code = request.POST.get('coupon_code', '').strip().upper()

    try:
        coupon = Coupon.objects.get(
            code=coupon_code,
            is_active=True
        )
    except Coupon.DoesNotExist:
        messages.error(
            request,
            'Invalid or inactive coupon code.'
        )
        return redirect('cart')

    # Check expiry
    if coupon.expiry_date < timezone.now():
        messages.error(
            request,
            'This coupon has expired.'
        )
        return redirect('cart')

    # Get cart
    cart_data = request.session.get('cart', {})

    if not cart_data:
        messages.error(
            request,
            'Your cart is empty.'
        )
        return redirect('cart')

    # Calculate cart subtotal
    cart_subtotal = Decimal('0.00')

    for food_id, quantity in cart_data.items():

        food = FoodItem.objects.get(id=food_id)

        item_total = food.price * quantity

        cart_subtotal += item_total

    # -----------------------------------------
    # Category-specific offers
    # -----------------------------------------

    offer_categories = {
        'PIZZA20': 'pizza',
        'BURGER15': 'burger'
    }

    if coupon_code in offer_categories:

        required_category = offer_categories[coupon_code]

        eligible_amount = Decimal('0.00')

        for food_id, quantity in cart_data.items():

            food = FoodItem.objects.get(id=food_id)

            item_total = food.price * quantity

            if food.category.strip().lower() == required_category:
                eligible_amount += item_total

        # No eligible item found
        if eligible_amount <= 0:
            messages.error(
                request,
                f'This offer is only valid on {required_category.title()} items.'
            )
            return redirect('cart')

    else:

        # Normal coupon applies to complete cart
        eligible_amount = cart_subtotal

    # -----------------------------------------
    # Minimum order amount
    # -----------------------------------------

    if cart_subtotal < coupon.minimum_order_amount:

        messages.error(
            request,
            f'Minimum order amount for this coupon is ₹{coupon.minimum_order_amount}.'
        )

        return redirect('cart')

    # -----------------------------------------
    # Calculate discount
    # -----------------------------------------

    discount = (
        eligible_amount
        * Decimal(coupon.discount_percent)
        / Decimal('100')
    )

    final_total = cart_subtotal - discount

    # Safety check
    if final_total < 0:
        final_total = Decimal('0.00')

    # -----------------------------------------
    # Save coupon details in session
    # -----------------------------------------

    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = str(discount)
    request.session['final_total'] = str(final_total)

    request.session.modified = True

    messages.success(
        request,
        f'Coupon {coupon.code} applied successfully! '
        f'You saved ₹{discount}.'
    )

    return redirect('cart')

def delivery_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    try:
        partner = DeliveryPartner.objects.get(
            user=request.user
        )
    except DeliveryPartner.DoesNotExist:
        messages.error(
            request,
            'You are not registered as a delivery partner.'
        )
        return redirect('home')

    orders = Order.objects.filter(
        delivery_partner=partner
    ).order_by('-created_at')

    return render(request, 'DeliveryDashboard.html', {
        'partner': partner,
        'orders': orders,
    })    
def update_delivery_status(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    try:
        partner = DeliveryPartner.objects.get(
            user=request.user
        )
    except DeliveryPartner.DoesNotExist:
        messages.error(
            request,
            'You are not registered as a delivery partner.'
        )
        return redirect('home')

    if request.method == 'POST':

        new_status = request.POST.get('status')

        allowed_statuses = [
            'Picked Up',
            'Out for Delivery',
            'Delivered',
        ]

        if new_status not in allowed_statuses:
            return redirect('delivery_dashboard')

        try:
            order = Order.objects.get(
                id=order_id,
                delivery_partner=partner
            )
        except Order.DoesNotExist:
            messages.error(
                request,
                'Order not found or not assigned to you.'
            )
            return redirect('delivery_dashboard')

        order.status = new_status
        order.save()

        # Create notification for customer
        if order.user:
            OrderNotification.objects.create(
                order=order,
                user=order.user,
                message=f'Your Order #{order.id} is now {new_status}.'
            )

        messages.success(
            request,
            f'Order #{order.id} status updated to {new_status}.'
        )

    return redirect('delivery_dashboard')

def admin_dashboard(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        messages.error(
            request,
            'You are not authorized to access the admin dashboard.'
        )
        return redirect('home')

# Delivery Partner ko Admin Dashboard access nahi milega
    if DeliveryPartner.objects.filter(user=request.user).exists():
        messages.error(
           request,
           'Delivery Partners cannot access the Admin Dashboard.'
    )
        return redirect('delivery_dashboard')

    total_orders = Order.objects.count()

    total_sales = Order.objects.filter(
        status='Delivered'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_food_items = FoodItem.objects.count()

    total_delivery_partners = DeliveryPartner.objects.count()
    delivery_partners = DeliveryPartner.objects.select_related('user').all()

    recent_orders = Order.objects.select_related(
        'delivery_partner'
    ).order_by('-created_at')[:10]

    daily_sales = list(
    Order.objects
    .filter(status='Delivered')
    .annotate(day=TruncDate('created_at'))
    .values('day')
    .annotate(sales=Sum('total_amount'))
    .order_by('day')
)

    if daily_sales:
        max_sales = max(item['sales'] for item in daily_sales)

    for item in daily_sales:
        if max_sales:
            item['percentage'] = float(item['sales']) / float(max_sales) * 100
        else:
            item['percentage'] = 0

    delivered_orders = Order.objects.filter(
    status='Delivered'
    ).count()

    pending_orders = Order.objects.exclude(
    status__in=['Delivered', 'Cancelled']
    ).count()

    cancelled_orders = Order.objects.filter(
    status='Cancelled'
    ).count()

    return render(
        request,
        'AdminDashboard.html',
        {
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_customers': total_customers,
            'total_food_items': total_food_items,
            'total_delivery_partners': total_delivery_partners,
            'delivery_partners': delivery_partners,
            'recent_orders': recent_orders,
            'delivered_orders': delivered_orders,
            'pending_orders': pending_orders,
            'cancelled_orders': cancelled_orders,
            'daily_sales': daily_sales,
        }
    )

def assign_delivery_partner(request, order_id):

    if not request.user.is_authenticated:
        return redirect('login')

    if not request.user.is_staff:
        messages.error(
            request,
            'You are not authorized to perform this action.'
        )
        return redirect('home')

    if request.method == 'POST':

        partner_id = request.POST.get('delivery_partner')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('admin_dashboard')

        if partner_id:
            try:
                partner = DeliveryPartner.objects.get(id=partner_id)
                order.delivery_partner = partner

                # If order is still newly placed,
                # keep its status as Order Placed.
                if order.status == 'Order Placed':
                    order.status = 'Order Placed'

                order.save()

                messages.success(
                    request,
                    f'Delivery Partner assigned to Order #{order.id}.'
                )

            except DeliveryPartner.DoesNotExist:
                messages.error(
                    request,
                    'Delivery Partner not found.'
                )

        else:
            order.delivery_partner = None
            order.save()

            messages.success(
                request,
                f'Delivery Partner removed from Order #{order.id}.'
            )

    return redirect('admin_dashboard')

def notifications(request):

    if not request.user.is_authenticated:
        return redirect('login')

    user_notifications = OrderNotification.objects.filter(
        user=request.user
    ).select_related(
        'order'
    ).order_by('-created_at')

    # Mark all notifications as read
    user_notifications.update(is_read=True)

    return render(request, 'Notifications.html', {
        'notifications': user_notifications
    })

def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(
                request,
                'No account found with this email address.'
            )
            return redirect('forgot_password')

        request.session['reset_user_id'] = user.id
        request.session.modified = True

        return redirect('set_new_password')

    return render(request, 'ForgotPassword.html')

def set_new_password(request):

    user_id = request.session.get('reset_user_id')

    if not user_id:
        messages.error(
            request,
            'Please enter your email first.'
        )
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.pop('reset_user_id', None)
        return redirect('forgot_password')

    if request.method == 'POST':

        new_password = request.POST.get('new_password1', '')
        confirm_password = request.POST.get('new_password2', '')

        if new_password != confirm_password:
            messages.error(
                request,
                'Passwords do not match.'
            )
            return redirect('set_new_password')

        if len(new_password) < 8:
            messages.error(
                request,
                'Password must be at least 8 characters long.'
            )
            return redirect('set_new_password')

        user.set_password(new_password)
        user.save()

        request.session.pop('reset_user_id', None)
        request.session.modified = True

        return redirect('password_reset_complete')

    return render(request, 'PasswordResetConfirm.html')        

def offer_order(request, coupon_code):
    coupon_code = coupon_code.strip().upper()

    try:
        coupon = Coupon.objects.get(
            code=coupon_code,
            is_active=True
        )
    except Coupon.DoesNotExist:
        messages.error(request, 'This offer is currently unavailable.')
        return redirect('offers')

    if coupon.expiry_date < timezone.now():
        messages.error(request, 'This offer has expired.')
        return redirect('offers')

    request.session['offer_code'] = coupon.code
    request.session.modified = True

    return redirect('menu')    