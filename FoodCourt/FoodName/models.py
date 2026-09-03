from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name