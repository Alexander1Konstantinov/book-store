# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User

# class LoginForm(AuthenticationForm):
#     username = forms.CharField(
#         label="Введите логин"
#     )
#     password = forms.CharField(label="Введите пароль", widget=forms.PasswordInput)
    
#     # def clean(self):
#     #     cleaned_data = super().clean()
        
#     #     username = cleaned_data.get("username")
#     #     password = cleaned_data.get("password")
        
#     #     users = User.objects.all()
#     #     if not users.filter(username = username):
#     #         raise forms.ValidationError("пользователя с таким логином не существует")
        
#     #     if password != users.filter(username = username)[0].password:
#     #         raise forms.ValidationError("Неверный пароль!")
        
#     #     return cleaned_data


# class RegisterForm(UserCreationForm):
#     username = forms.CharField(
#         label="Введите логин",
#     )
#     password = forms.CharField(label="Введите пароль", widget=forms.PasswordInput)
#     second_password = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)
    
#     # def clean(self):
#     #     cleaned_data = super().clean()
        
#     #     username = cleaned_data.get("username")
#     #     password = cleaned_data.get("password")
#     #     second_password = cleaned_data.get("second_password")
        
#     #     users = User.objects.all()
        
#     #     if users.filter(username = username):
#     #         raise forms.ValidationError("Такой логин занят")
            
#     #     if password and second_password and password != second_password:
#     #         raise forms.ValidationError("Пароли не совпадают!")
        
#     #     return cleaned_data

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'shipping_address', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван Иванов'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivan@example.com'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Полный адрес доставки',
                'rows': 4
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Дополнительные пожелания к заказу',
                'rows': 3
            }),
        }
        labels = {
            'customer_name': 'ФИО',
            'customer_email': 'Email',
            'customer_phone': 'Телефон',
            'shipping_address': 'Адрес доставки',
            'notes': 'Комментарий к заказу'
        }