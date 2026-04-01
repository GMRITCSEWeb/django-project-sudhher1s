import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CartItem, Product, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product", None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if self.product and quantity > self.product.stock:
            raise forms.ValidationError("Requested quantity exceeds available stock.")
        return quantity


class CartItemUpdateForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ("quantity",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity"].min_value = 1

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > self.instance.product.stock:
            raise forms.ValidationError("Quantity cannot exceed product stock.")
        return quantity


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"^\+?[0-9]{10,15}$", phone):
            raise forms.ValidationError("Enter a valid phone number with 10 to 15 digits.")
        return phone


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("address", "phone", "role")


class SellerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "product_type", "price", "stock", "category", "image", "is_active")
