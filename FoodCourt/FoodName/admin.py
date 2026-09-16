from django.contrib import admin
from .models import FoodItem, Order, OrderItem, FoodReview, Coupon, DeliveryPartner


admin.site.register(FoodReview)

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
        'delivery_partner',
        'status',
        'created_at'
    )

    list_filter = ('status', 'payment_method', 'created_at')

    search_fields = ('name', 'phone', 'email')

    inlines = [OrderItemInline]


admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Order, OrderAdmin)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount_percent',
        'minimum_order_amount',
        'expiry_date',
        'is_active',
    )

    list_filter = ('is_active',)

    search_fields = ('code',)

@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'phone',
        'is_available',
        'created_at',
    )

    list_filter = (
        'is_available',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'phone',
    )    
