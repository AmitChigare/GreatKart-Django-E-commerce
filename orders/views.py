from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
import datetime
import json
from django.contrib.auth.decorators import login_required

# Order Email
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        status=body["status"],
        amount_paid=body["amount_paid"],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Send(Add) order details to orderProduct
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)

        order_product.variations.set(product_variation)
        order_product.save()

        # Reduce the product quantity
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send a confirmation email to user
    mail_subject = "Thank you for Ordering."
    message = render_to_string(
        "orders/order_received_email.html",
        {"user": request.user, "order": order},
    )
    to_mail = request.user.email
    send_mail = EmailMessage(mail_subject, message, to=[to_mail])
    send_mail.send()

    # Send orderId and TrandId back to payments.html page via json (then)
    data = {"order_number": order.order_number, "transId": payment.payment_id}

    return JsonResponse(data)
    # Body: {'orderID': '2023012856', 'transID': '4WM648932R1630139', 'status': 'COMPLETED', 'payment_method': 'Paypal'}


@login_required(login_url="login")
def place_order(request, total=0, quantity=0, delivery_charge=0, cart_items=None):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if cart_items.count() <= 0:
        return redirect("store")

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (5 * total) / 100
    grand_total = total + tax
    if grand_total <= 1000 and grand_total > 0:
        delivery_charge = 40
    grand_total = total + tax + delivery_charge

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.user = current_user
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.address_line = form.cleaned_data["address_line"]
            data.postal_code = form.cleaned_data["postal_code"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()

            # Order number generator
            yr = int(datetime.date.today().strftime("%Y"))
            mt = int(datetime.date.today().strftime("%m"))
            dt = int(datetime.date.today().strftime("%d"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            context = {
                "order": order,
                "cart_items": cart_items,
                "tax": tax,
                "total": grand_total,
                "delivery_charge": delivery_charge,
            }

            return render(request, "orders/payments.html", context)
    return HttpResponse("ok")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transId = request.GET.get("payment_id")
    payment = Payment.objects.get(payment_id=transId)

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        context = {
            "order": order,
            "ordered_products": ordered_products,
            "payment": payment,
            "subtotal": subtotal,
        }
        return render(request, "orders/order_complete.html", context)
    except (Product.DoesNotExist, Order.DoesNotExist):
        return redirect("home")


# {
#   "id": "52R13947R0801100A",
#   "intent": "CAPTURE",
#   "status": "COMPLETED",
#   "purchase_units": [
#     {
#       "reference_id": "default",
#       "amount": {
#         "currency_code": "USD",
#         "value": "77.44"
#       },
#       "payee": {
#         "email_address": "sandox.business@greatkart.io",
#         "merchant_id": "W7N4PPLY6KRNJ"
#       },
#       "shipping": {
#         "name": {
#           "full_name": "Amit Amith"
#         },
#         "address": {
#           "address_line_1": "1 Main St",
#           "admin_area_2": "San Jose",
#           "admin_area_1": "CA",
#           "postal_code": "95131",
#           "country_code": "US"
#         }
#       },
#       "payments": {
#         "captures": [
#           {
#             "id": "1Y28202120759312U",
#             "status": "COMPLETED",
#             "amount": {
#               "currency_code": "USD",
#               "value": "77.44"
#             },
#             "final_capture": true,
#             "seller_protection": {
#               "status": "ELIGIBLE",
#               "dispute_categories": [
#                 "ITEM_NOT_RECEIVED",
#                 "UNAUTHORIZED_TRANSACTION"
#               ]
#             },
#             "create_time": "2023-01-27T14:48:58Z",
#             "update_time": "2023-01-27T14:48:58Z"
#           }
#         ]
#       }
#     }
#   ],
#   "payer": {
#     "name": {
#       "given_name": "Amit",
#       "surname": "Amith"
#     },
#     "email_address": "sandox.personal1@greatkart.io",
#     "payer_id": "L7FKJCACJWJ9U",
#     "address": {
#       "country_code": "US"
#     }
#   },
#   "create_time": "2023-01-27T14:48:30Z",
#   "update_time": "2023-01-27T14:48:58Z",
#   "links": [
#     {
#       "href": "https://api.sandbox.paypal.com/v2/checkout/orders/52R13947R0801100A",
#       "rel": "self",
#       "method": "GET"
#     }
#   ]
# }
