from django.contrib import admin
from django.urls import path
from FoodName import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('delivery-dashboard/',views.delivery_dashboard,name='delivery_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('assign-delivery-partner/<int:order_id>/',views.assign_delivery_partner,name='assign_delivery_partner'),
    path('delivery-status/<int:order_id>/',views.update_delivery_status,name='update_delivery_status'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('reviews/', views.reviews, name='reviews'),
    path('cart/', views.cart, name='cart'),
    path('apply-coupon/',views.apply_coupon,name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('increase-cart/<int:food_id>/', views.increase_cart, name='increase_cart'),
    path('decrease-cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
    path('menu-increase/<int:food_id>/', views.menu_increase_cart, name='menu_increase_cart'),
    path('menu-decrease/<int:food_id>/', views.menu_decrease_cart, name='menu_decrease_cart'),
    path('remove-from-cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('offers/', views.offers, name='offers'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.user_logout, name='logout'),
    path('save-checkout-details/', views.save_checkout_details, name='save_checkout_details'),
    path('demo-payment/', views.demo_payment, name='demo_payment'),
    path('demo-payment-success/', views.demo_payment_success, name='demo_payment_success'),
    path('notifications/',views.notifications,name='notifications'),
    path('forgot-password/',views.forgot_password,name='forgot_password'),
    path('set-new-password/',views.set_new_password,name='set_new_password'),
    path('password-reset-success/',auth_views.PasswordResetCompleteView.as_view(    template_name='PasswordResetComplete.html'),name='password_reset_complete'),
    path(
    'offer-order/<str:coupon_code>/',
    views.offer_order,
    name='offer_order'
),
]