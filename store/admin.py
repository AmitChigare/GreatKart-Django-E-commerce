from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "slug",
        "category",
        "price",
        "is_available",
        "created_date",
        "modified_date",
    )
    list_display_links = ("product_name", "slug")
    prepopulated_fields = {"slug": ("product_name",)}


class VariationAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "variation_category",
        "variation_value",
        "is_active",
    )
    list_editable = ("is_active",)
    list_filter = (
        "product",
        "variation_category",
        "variation_value",
        "is_active",
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
