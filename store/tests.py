from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Category, Order, OrderItem, Product, UserProfile
from .templatetags.store_tags import top_products

class BasicTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(username="buyer1", password="buyer-pass-123")
        self.seller = User.objects.create_user(username="seller1", password="seller-pass-123")
        seller_profile = UserProfile.objects.get(user=self.seller)
        seller_profile.role = UserProfile.ROLE_SELLER
        seller_profile.save(update_fields=["role"])

        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Phone",
            description="A sample product",
            price="100.00",
            stock=5,
            category=self.category,
            seller=self.seller,
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'store/product_list.html')

    def test_product_detail_page(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)

    def test_non_seller_cannot_access_seller_dashboard(self):
        self.client.login(username="buyer1", password="buyer-pass-123")
        response = self.client.get(reverse("seller_dashboard"))
        self.assertRedirects(response, reverse("product_list"))

    def test_seller_can_create_product(self):
        self.client.login(username="seller1", password="seller-pass-123")
        payload = {
            "name": "Campus Keyboard",
            "description": "Mechanical keyboard",
            "product_type": "code",
            "price": "49.99",
            "stock": 7,
            "category": self.category.id,
            "is_active": True,
        }
        response = self.client.post(reverse("seller_product_create"), payload)
        self.assertRedirects(response, reverse("seller_dashboard"))
        self.assertTrue(Product.objects.filter(name="Campus Keyboard", seller=self.seller).exists())

    def test_checkout_creates_order_and_reduces_stock(self):
        self.client.login(username="buyer1", password="buyer-pass-123")
        CartItem.objects.create(user=self.buyer, product=self.product, quantity=2)

        response = self.client.post(
            reverse("checkout"),
            {
                "full_name": "Buyer One",
                "email": "buyer@example.com",
                "phone": "9876543210",
                "address": "Hostel Block A",
            },
        )
        order = Order.objects.get(user=self.buyer)
        self.assertRedirects(response, reverse("order_confirmation", kwargs={"order_id": order.id}))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(order.items.count(), 1)
        self.assertFalse(CartItem.objects.filter(user=self.buyer).exists())

    def test_product_status_api_returns_live_data(self):
        response = self.client.get(reverse("product_status_api", kwargs={"slug": self.product.slug}))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], self.product.name)
        self.assertEqual(payload["stock"], self.product.stock)

    def test_admin_dashboard_requires_staff(self):
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin-panel/", response.url)

        self.client.login(username="buyer1", password="buyer-pass-123")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/products/", response.url)

    def test_admin_dashboard_access_for_staff(self):
        admin_user = User.objects.create_user(username="admin1", password="admin-pass-123", is_staff=True)
        self.client.login(username="admin1", password="admin-pass-123")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_top_products_sorted_by_sales(self):
        other_product = Product.objects.create(
            name="Budget Mouse",
            description="Wireless mouse",
            price="25.00",
            stock=10,
            category=self.category,
            seller=self.seller,
        )
        order = Order.objects.create(
            user=self.buyer,
            full_name="Buyer One",
            email="buyer@example.com",
            phone="9876543210",
            address="Hostel Block A",
            total_amount="0.00",
        )
        OrderItem.objects.create(order=order, product=other_product, quantity=4, price=other_product.price)
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price=self.product.price)

        top_products_list = list(top_products(5)["top_products"])
        self.assertEqual(top_products_list[0].id, other_product.id)
