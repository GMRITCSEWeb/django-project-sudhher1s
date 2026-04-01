from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
	name = models.CharField(max_length=120)
	slug = models.SlugField(max_length=140, unique=True, blank=True)
	parent = models.ForeignKey(
		"self",
		on_delete=models.CASCADE,
		related_name="children",
		null=True,
		blank=True,
	)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "categories"

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("product_by_category", kwargs={"slug": self.slug})

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)
			slug = base_slug
			counter = 1
			while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)


class Product(models.Model):
	TYPE_CODE = "code"
	TYPE_PAPER = "paper"
	TYPE_PROJECT = "project"
	TYPE_INTERNSHIP = "internship"
	TYPE_OTHER = "other"

	TYPE_CHOICES = [
		(TYPE_CODE, "Code"),
		(TYPE_PAPER, "Papers"),
		(TYPE_PROJECT, "Projects"),
		(TYPE_INTERNSHIP, "Internships"),
		(TYPE_OTHER, "Other Academic Resource"),
	]

	name = models.CharField(max_length=180)
	slug = models.SlugField(max_length=200, unique=True, blank=True)
	description = models.TextField()
	product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CODE)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
	seller = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="products_for_sale",
		null=True,
		blank=True,
	)
	is_active = models.BooleanField(default=True)
	image = models.ImageField(upload_to="products/", null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("product_detail", kwargs={"slug": self.slug})

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)
			slug = base_slug
			counter = 1
			while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)


class UserProfile(models.Model):
	ROLE_BUYER = "buyer"
	ROLE_SELLER = "seller"

	ROLE_CHOICES = [
		(ROLE_BUYER, "Buyer"),
		(ROLE_SELLER, "Seller"),
	]

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	address = models.TextField(blank=True)
	phone = models.CharField(max_length=15, blank=True)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_BUYER)

	def __str__(self):
		return f"Profile: {self.user.username}"


class CartItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
	quantity = models.PositiveIntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		unique_together = ("user", "product")

	def __str__(self):
		return f"{self.user.username} - {self.product.name} ({self.quantity})"

	@property
	def subtotal(self):
		return self.product.price * self.quantity


class Order(models.Model):
	STATUS_PENDING = "pending"
	STATUS_SHIPPED = "shipped"
	STATUS_DELIVERED = "delivered"

	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_SHIPPED, "Shipped"),
		(STATUS_DELIVERED, "Delivered"),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
	full_name = models.CharField(max_length=150)
	email = models.EmailField()
	phone = models.CharField(max_length=15)
	address = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
	quantity = models.PositiveIntegerField(default=1)
	price = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f"Order #{self.order.id} - {self.product.name}"

	@property
	def subtotal(self):
		return self.price * self.quantity
