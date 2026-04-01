from django.contrib import admin

from .models import CartItem, Category, Order, OrderItem, Product, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    search_fields = ("name", "slug")
    list_filter = ("parent",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("name", "seller", "category", "price", "stock", "is_active", "created_at")
	search_fields = ("name", "slug", "description")
	list_filter = ("category", "is_active", "created_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role", "phone")
	search_fields = ("user__username", "phone")
	list_filter = ("role",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ("user", "product", "quantity", "created_at")
	search_fields = ("user__username", "product__name")
	list_filter = ("created_at",)


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ("product", "quantity", "price")
	can_delete = False


@admin.action(description="Mark selected orders as shipped")
def mark_as_shipped(modeladmin, request, queryset):
	queryset.update(status=Order.STATUS_SHIPPED)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "full_name", "status", "total_amount", "created_at")
	list_filter = ("status", "created_at")
	search_fields = ("id", "user__username", "full_name", "email", "phone")
	date_hierarchy = "created_at"
	readonly_fields = ("user", "full_name", "email", "phone", "address", "total_amount", "created_at")
	actions = (mark_as_shipped,)
	inlines = (OrderItemInline,)

	def has_delete_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("order", "product", "quantity", "price")
	list_filter = ("order__status",)
