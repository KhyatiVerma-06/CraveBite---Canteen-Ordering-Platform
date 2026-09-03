from django.contrib import admin
from django.urls import path
from FoodName import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('increase-cart/<int:food_id>/', views.increase_cart, name='increase_cart'),
    path('decrease-cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-from-cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('offers/', views.offers, name='offers'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
]
