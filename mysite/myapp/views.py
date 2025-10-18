from django.forms import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.views import generic
from django.views.generic import DetailView
from django.contrib import messages

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect

from .forms import *


def index(request):
    is_authenticated = request.user.is_authenticated
    username = request.user.username if is_authenticated else None

    return render(
        request,
        "index.html",
        {"is_authenticated": is_authenticated, "username": username},
    )


def about(request):
    return HttpResponse("О сайте")


def contact(request):
    return HttpResponse("Контакты")


def logout_view(request):
    logout(request)

    return redirect("home")


def my_login(request):
    if request.method == "POST":
        userform = AuthenticationForm(request, data=request.POST)

        if userform.is_valid():
            username = userform.cleaned_data["username"]
            password = userform.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect("home")
        else:
            return render(
                request, "login.html", {"form": userform, "url_val": "url login"}
            )
    else:
        userform = AuthenticationForm()
        return render(request, "login.html", {"form": userform, "url_val": "url login"})


def register(request):
    if request.method == "POST":
        userform = UserCreationForm(request.POST)
        if userform.is_valid():
            user = userform.save()
            login(request, user)

            return redirect("home")
        else:
            return render(
                request, "login.html", {"form": userform, "url_val": "url register"}
            )
    else:
        userform = UserCreationForm()
        return render(
            request, "login.html", {"form": userform, "url_val": "url register"}
        )


class BookListView(generic.ListView):
    model = Book
    context_object_name = "books"
    template_name = "book_list.html"
    paginate_by = 10


class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    context_object_name = "book"


# Или функция для детальной страницы
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, "book_detail.html", {"book": book})


# # # Функция покупки (заглушка)
# def buy_book(request, book_id):
#     book = get_object_or_404(Book, id=book_id)

#     # Здесь будет логика оформления покупки
#     # Пока просто сообщение об успехе
#     return render(request, 'purchase_success.html', {'book': book})


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))

    # Получаем или создаем корзину для пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Проверяем, есть ли уже эта книга в корзине
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, book=book, defaults={"quantity": quantity}
    )

    if not item_created:
        # Если книга уже в корзине, увеличиваем количество
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(
            request, f"Количество книги '{book.title}' обновлено в корзине"
        )
    else:
        messages.success(request, f"Книга '{book.title}' добавлена в корзину")

    return redirect("cart_detail")


@login_required
def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    context = {
        "cart": cart,
        "cart_items": cart_items,
    }
    return render(request, "cart/cart_detail.html", context)


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update":
            quantity = int(request.POST.get("quantity", 1))
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Количество обновлено")
            else:
                cart_item.delete()
                messages.success(request, "Товар удален из корзины")

        elif action == "remove":
            cart_item.delete()
            messages.success(request, "Товар удален из корзины")

    return redirect("cart_detail")


@login_required
def clear_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        messages.success(request, "Корзина очищена")
    except Cart.DoesNotExist:
        pass

    return redirect("cart_detail")


@login_required
def checkout(request):
    """Страница оформления заказа"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, "Ваша корзина пуста")
        return redirect("cart_detail")

    if not cart_items:
        messages.error(request, "Ваша корзина пуста")
        return redirect("cart_detail")

    total_price = cart.total_price()

    # Предзаполняем форму данными пользователя
    initial_data = {
        "customer_name": f"{request.user.first_name} {request.user.last_name}".strip(),
        "customer_email": request.user.email,
        "customer_phone": "",
        "shipping_address": "",
        "notes": "",
    }

    if request.method == "POST":
        form = OrderForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            order.save()

            # Переносим товары из корзины в заказ
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    price=cart_item.book.price,
                )

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(request, f"Заказ #{order.id} успешно оформлен!")
            return redirect("order_detail", order_id=order.id)
    else:
        form = OrderForm(initial=initial_data)

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "total_price": total_price,
        "form": form,
    }
    return render(request, "orders/checkout.html", context)


@login_required
def order_detail(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    context = {"order": order, "order_items": order_items}
    return render(request, "orders/order_detail.html", context)


@login_required
def order_list(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    context = {"orders": orders}
    return render(request, "orders/order_list.html", context)


@login_required
def cancel_order(request, order_id):
    """Отмена заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "pending":
        order.status = "cancelled"
        order.save()
        messages.success(request, f"Заказ #{order.id} отменен")
    else:
        messages.error(request, "Невозможно отменить заказ в текущем статусе")

    return redirect("order_detail", order_id=order.id)
