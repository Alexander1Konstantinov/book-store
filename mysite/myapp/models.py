from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        if sum(item.total_price() for item in self.items.all()) >= 1000:
            return sum(item.total_price() for item in self.items.all())
        else:
            return sum(item.total_price() for item in self.items.all()) + 250

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает обработки"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Информация о доставке
    shipping_address = models.TextField()
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    # Комментарий к заказу
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"

    def get_status_display_class(self):
        status_classes = {
            "pending": "warning",
            "processing": "info",
            "shipped": "primary",
            "delivered": "success",
            "cancelled": "danger",
        }
        return status_classes.get(self.status, "secondary")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"
