from django.contrib import admin
from .models import FoodItem, Order, OrderItem


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'price')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'phone',
        'email',
        'payment_method',
        'total_amount',
        'status',
        'created_at'
    )

    list_filter = ('status', 'payment_method', 'created_at')

    search_fields = ('name', 'phone', 'email')

    inlines = [OrderItemInline]


admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Order, OrderAdmin)