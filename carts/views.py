from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # Get product
    product_variation = []
    if request.method == "POST":
        # color = request.POST["color"]
        # size = request.POST["size"]
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)

        ex_var_list = []
        iid = []
        for item in cart_item:
            existing_variable = item.variations.all()
            ex_var_list.append(list(existing_variable))
            iid.append(item.id)

        print(ex_var_list)

        if product_variation in ex_var_list:
            iindex = ex_var_list.index(product_variation)
            item_id = iid[iindex]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()

        else:
            item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()

    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    # try:
    #     cart_item = CartItem.objects.get(product=product)
    #     if len(product_variation) > 0:
    #         cart_item.variations.clear()
    #         for item in product_variation:
    #             cart_item.variations.add(item)
    #     cart_item.quantity += 1
    #     cart_item.save()
    # except CartItem.DoesNotExist:
    #     cart_item = CartItem.objects.create(
    #         product=product,
    #         quantity=1,
    #         cart=cart,
    #     )
    #     if len(product_variation) > 0:
    #         cart_item.variations.clear()
    #         for item in product_variation:
    #             cart_item.variations.add(item)
    #     cart_item.save()

    # print(request.get_full_path())
    # print(request.META.get("HTTP_REFERER"))
    if "cart" not in request.META["HTTP_REFERER"]:
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
        delivery_charge = 0
        tax = 0
        grand_total = 0

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


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")


def remove_cart_items(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    messages.success(request, "Removed ✅")
    return redirect("cart")
