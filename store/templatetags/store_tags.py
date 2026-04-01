from django import template
from django.db.models import Sum
from django.db.models.functions import Coalesce

from store.models import Product

register = template.Library()


@register.inclusion_tag("store/components/top_products.html")
def top_products(limit=5):
    products = (
        Product.objects.select_related("category")
        .filter(is_active=True)
        .annotate(total_sold=Coalesce(Sum("order_items__quantity"), 0))
        .order_by("-total_sold", "-created_at")[:limit]
    )
    return {"top_products": products}
