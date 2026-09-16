from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    delivery_partner = models.ForeignKey(
    'DeliveryPartner',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='orders'
)
     
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    payment_method = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
    max_length=50,
    choices=[
        ('Order Placed', 'Order Placed'),
        ('Preparing', 'Preparing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ],
    default='Order Placed'
)

    def __str__(self):
        return f'Order #{self.id} - {self.name}'

class OrderNotification(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,        related_name='notifications'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.food.name} x {self.quantity}'    

class FoodReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(
    FoodItem,
    on_delete=models.CASCADE,
    related_name='reviews'
)

    rating = models.PositiveIntegerField(
        choices=[
            (1, '⭐ 1 Star'),
            (2, '⭐⭐ 2 Stars'),
            (3, '⭐⭐⭐ 3 Stars'),
            (4, '⭐⭐⭐⭐ 4 Stars'),
            (5, '⭐⭐⭐⭐⭐ 5 Stars'),
        ]
    )

    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.food.name} - {self.rating} Stars by {self.user.username}'

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField()
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code   

class DeliveryPartner(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username         