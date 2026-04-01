from django.db.models import Count

from .models import Product


# Filter products that are in stock.
in_stock_products = Product.objects.filter(stock__gt=0)

# Exclude products that are out of stock.
available_products = Product.objects.exclude(stock=0)

# Annotate products with category product counts.
products_with_category_size = Product.objects.select_related("category").annotate(
    category_product_count=Count("category__products")
)
