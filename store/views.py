from decimal import Decimal
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import (
    AddToCartForm,
    CartItemUpdateForm,
    CheckoutForm,
    ProfileForm,
    RegisterForm,
    SellerProductForm,
)
from .models import CartItem, Category, Order, OrderItem, Product, UserProfile


STUDENT_CATEGORY_NAMES = ["Code", "Papers", "Projects", "Internships"]


def ensure_student_categories():
    for category_name in STUDENT_CATEGORY_NAMES:
        Category.objects.get_or_create(name=category_name)


def serialize_product(product):
    return {
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "category": product.category.name,
        "product_type": product.get_product_type_display(),
        "seller": product.seller.username if product.seller else "Campus Seller",
        "detail_url": product.get_absolute_url(),
        "image_url": product.image.url if product.image else "",
    }


def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.role != UserProfile.ROLE_SELLER:
            messages.error(request, "Seller access required for this page.")
            return redirect("product_list")
        return view_func(request, *args, **kwargs)

    return login_required(wrapper)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_staff, login_url="product_list")(view_func))


class ProductListView(ListView):
    model = Product
    template_name = "store/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.select_related("category", "seller").filter(is_active=True)

    def get_context_data(self, **kwargs):
        ensure_student_categories()
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.select_related("parent").all()
        context["active_category"] = None
        context["search_query"] = ""
        context["react_products"] = [serialize_product(product) for product in context["products"]]
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.select_related("category", "seller").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.select_related("parent").all()
        context["add_to_cart_form"] = AddToCartForm(product=self.object)
        return context


def category_products(request, slug):
    ensure_student_categories()
    category = get_object_or_404(Category.objects.select_related("parent"), slug=slug)
    child_ids = category.children.values_list("id", flat=True)
    products = (
        Product.objects.select_related("category", "seller")
        .filter(is_active=True)
        .filter(Q(category=category) | Q(category__id__in=child_ids))
        .distinct()
    )

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "categories": Category.objects.select_related("parent").all(),
            "active_category": category,
            "search_query": "",
            "is_paginated": False,
            "react_products": [serialize_product(product) for product in products],
        },
    )


def search_products(request):
    ensure_student_categories()
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category", "seller").filter(is_active=True)
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "categories": Category.objects.select_related("parent").all(),
            "active_category": None,
            "search_query": query,
            "is_paginated": False,
            "react_products": [serialize_product(product) for product in products],
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("product_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save(update_fields=["role"])
            login(request, user)
            messages.success(request, "Registration successful. Welcome to CodeMart!")
            return redirect("product_list")
    else:
        form = RegisterForm()
    return render(request, "store/register.html", {"form": form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "store/profile.html", {"form": form})


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product.objects.filter(is_active=True), slug=slug)
    form = AddToCartForm(request.POST or None, product=product)
    if request.method == "POST" and form.is_valid():
        quantity = form.cleaned_data["quantity"]
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, "Not enough stock for that quantity.")
                return redirect("product_detail", slug=slug)
            cart_item.quantity = new_quantity
            cart_item.save()
        messages.success(request, f"{product.name} added to cart.")
    else:
        messages.error(request, "Unable to add item to cart.")
    return redirect("product_detail", slug=slug)


@login_required
def cart_view(request):
    cart_items = CartItem.objects.select_related("product").filter(user=request.user)
    total = sum((item.subtotal for item in cart_items), Decimal("0.00"))
    return render(
        request,
        "store/cart.html",
        {"cart_items": cart_items, "total": total},
    )


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    form = CartItemUpdateForm(request.POST, instance=cart_item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cart item updated.")
    else:
        messages.error(request, "Could not update quantity.")
    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


@login_required
@transaction.atomic
def checkout_view(request):
    cart_items = list(CartItem.objects.select_related("product").filter(user=request.user))
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("product_list")

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    initial_data = {
        "full_name": request.user.get_full_name() or request.user.username,
        "email": request.user.email,
        "phone": profile.phone,
        "address": profile.address,
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            for item in cart_items:
                if not item.product.is_active:
                    messages.error(request, f"{item.product.name} is no longer available.")
                    return redirect("cart")
                if item.quantity > item.product.stock:
                    messages.error(request, f"Insufficient stock for {item.product.name}.")
                    return redirect("cart")

            order = Order.objects.create(user=request.user, **form.cleaned_data)
            total = Decimal("0.00")

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
                item.product.stock -= item.quantity
                item.product.save(update_fields=["stock"])
                total += item.product.price * item.quantity

            order.total_amount = total
            order.save(update_fields=["total_amount"])

            CartItem.objects.filter(user=request.user).delete()
            messages.success(request, "Order placed successfully.")
            return redirect("order_confirmation", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial_data)

    total = sum((item.subtotal for item in cart_items), Decimal("0.00"))
    return render(
        request,
        "store/checkout.html",
        {"form": form, "cart_items": cart_items, "total": total},
    )


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product").select_related("user"),
        id=order_id,
        user=request.user,
    )
    return render(request, "store/order_confirmation.html", {"order": order})


@login_required
def buyer_orders_view(request):
    orders = Order.objects.prefetch_related("items__product").filter(user=request.user)
    return render(request, "store/buyer_orders.html", {"orders": orders})


@seller_required
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user).select_related("category")
    stats = products.aggregate(
        total_products=Count("id"),
        active_products=Count("id", filter=Q(is_active=True)),
        total_stock=Sum("stock"),
    )
    recent_orders = (
        OrderItem.objects.select_related("product", "order", "order__user")
        .filter(product__seller=request.user)
        .order_by("-order__created_at")[:10]
    )
    return render(
        request,
        "store/seller_dashboard.html",
        {
            "products": products,
            "stats": stats,
            "recent_orders": recent_orders,
        },
    )


@seller_required
def seller_product_create(request):
    ensure_student_categories()
    if request.method == "POST":
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product created successfully.")
            return redirect("seller_dashboard")
    else:
        form = SellerProductForm()
    return render(request, "store/seller_product_form.html", {"form": form, "is_edit": False})


@seller_required
def seller_product_edit(request, slug):
    ensure_student_categories()
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    if request.method == "POST":
        form = SellerProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("seller_dashboard")
    else:
        form = SellerProductForm(instance=product)
    return render(request, "store/seller_product_form.html", {"form": form, "is_edit": True, "product": product})


@seller_required
def seller_product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug, seller=request.user)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("seller_dashboard")
    return render(request, "store/seller_product_delete.html", {"product": product})


@seller_required
def seller_orders_view(request):
    order_items = (
        OrderItem.objects.select_related("order", "order__user", "product")
        .filter(product__seller=request.user)
        .order_by("-order__created_at")
    )
    return render(request, "store/seller_orders.html", {"order_items": order_items})


@admin_required
def admin_dashboard(request):
    totals = {
        "users": User.objects.count(),
        "sellers": UserProfile.objects.filter(role=UserProfile.ROLE_SELLER).count(),
        "buyers": UserProfile.objects.filter(role=UserProfile.ROLE_BUYER).count(),
        "products": Product.objects.count(),
        "active_products": Product.objects.filter(is_active=True).count(),
        "orders": Order.objects.count(),
    }

    revenue = Order.objects.aggregate(total=Coalesce(Sum("total_amount"), Decimal("0.00")))["total"]
    low_stock_products = Product.objects.filter(is_active=True, stock__lte=5).order_by("stock", "name")[:10]
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:10]

    return render(
        request,
        "store/admin_dashboard.html",
        {
            "totals": totals,
            "revenue": revenue,
            "low_stock_products": low_stock_products,
            "recent_orders": recent_orders,
        },
    )


def product_status_api(request, slug):
    product = get_object_or_404(Product.objects.filter(is_active=True), slug=slug)
    return JsonResponse(
        {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "stock": product.stock,
            "product_type": product.get_product_type_display(),
            "is_active": product.is_active,
            "updated_at": product.updated_at.isoformat(),
        }
    )
