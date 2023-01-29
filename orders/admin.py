from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = [
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "ordered",
        "variations",
    ]
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "full_name",
        "phone",
        "postal_code",
        "order_total",
        "status",
        "is_ordered",
        "created_at",
    ]
    list_filter = ["status", "is_ordered", "email"]
    search_fields = [
        "order_number",
        "full_name",
        "phone",
        "email",
        "postal_code",
    ]
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
