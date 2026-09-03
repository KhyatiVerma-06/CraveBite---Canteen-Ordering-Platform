from django.contrib import admin
from . models import FoodItem


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'price')
admin.site.register(FoodItem, FoodItemAdmin)
