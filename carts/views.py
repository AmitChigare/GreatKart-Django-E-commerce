from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    if request.method == "POST":
        color = request.POST["color"]
        size = request.POST["size"]
        print(color, size)
    product = Product.objects.get(id=product_id)  # Get product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        cart_item.save()
    # print(request.get_full_path())
    # print(request.META.get("HTTP_REFERER"))
    messages.success(request, "Added to cart ✅")
    return redirect(request.META.get("HTTP_REFERER"))
    # if "cart" in request.META.get("HTTP_REFERER"):
    #     return redirect("cart")
    # elif "store" in request.META.get("HTTP_REFERER"):
    #     return redirect(
    #         "product_detail",
    #         category_slug=product.category.slug,
    #         product_slug=product.slug,
    #     )


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (5 * total) / 100
        grand_total = total + tax
        delivery_charge = 0
        if grand_total <= 1000 and grand_total > 0:
            delivery_charge = 40
    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "delivery_charge": delivery_charge,
        "tax": tax,
        "grand_total": grand_total + delivery_charge,
    }
    # print(cart_items)
    return render(request, "cart.html", context)


def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect("cart")


def remove_cart_items(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    messages.success(request, "Removed ✅")
    return redirect("cart")
