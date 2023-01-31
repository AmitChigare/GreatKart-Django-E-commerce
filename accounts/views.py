from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification Email, User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct
from .forms import UserForm, UserProfileForm

default_dp = "./img_avatar.png"

# import requests

# Create your views here.
def register(request):
    if request.method == "POST":
        # form1 = request.POST
        # print(form1["first_name"])
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                password=password,
                username=username,
                email=email,
            )
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "[GreatKart]Activate your account"
            message = render_to_string(
                "accounts/acc_activation.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_mail = email
            send_mail = EmailMessage(mail_subject, message, to=[to_mail])
            send_mail.send()

            messages.success(request, "Check your email to activate your account.")
            return redirect("/accounts/login?command=verification&email=" + email)

    else:
        form = RegistrationForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    iid = []
                    for item in cart_item:
                        existing_variance = item.variations.all()
                        ex_var_list.append(list(existing_variance))
                        iid.append(item.id)

                    for pv in product_variation:
                        if pv in ex_var_list:
                            index = ex_var_list.index(pv)
                            item_id = iid[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            auth.login(request, user)
            messages.success(request, "Logged in successfully")
            # return redirect(request.META.get("HTTP_REFERER"))
            # url = request.META.get("HTTP_REFERER")
            # try:
            #     query = requests.utils.urlparse(url).query()
            #     params = dict(x.split("=") for x in query.split("&"))
            #     if "next" in params:
            #         return redirect(params["next"])
            # except:
            #     return redirect("home")
            return redirect("home")
        else:
            messages.warning(request, "Invalid email or password")
            return redirect("login")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Logged out.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated")
        return redirect("login")
    else:
        messages.warning(request, "Invalid activation link.")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "created_at"
    )
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    order_count = orders.count()
    context = {"order_count": order_count, "user_profile": user_profile}
    return render(request, "accounts/dashboard.html", context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # FORGOT PASSWORD
            current_site = get_current_site(request)
            mail_subject = "[GreatKart]Reset your Password"
            message = render_to_string(
                "accounts/forgotPassActivation.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_mail = email
            send_mail = EmailMessage(mail_subject, message, to=[to_mail])
            send_mail.send()

            messages.success(request, "Please check your email to reset your password.")
            return redirect("login")
        else:
            messages.warning(request, "Account not found with that email")
            return redirect("forgotPassword")

    return render(request, "accounts/forgotPassword.html")


def resetpass_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password.")
        return redirect("resetPassword")
    else:
        messages.warning(request, "Link is Invalid or is expired")
        return redirect("login")


def resetPassword(request):
    # try:
    #     uid = request.session["uid"]
    # except (KeyError, TypeError):
    #     messages.warning(request, "You are not authenticated!!!")
    #     return redirect("home")
    # return redirect(request.META.get("HTTP_REFERER"))
    # http://localhost:8000/accounts/resetPassword/
    # for use in func return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    # for use in template <a href="{{request.META.HTTP_REFERER}}">Go Back</a>
    if request.method == "POST":
        password = request.POST["password"]
        confirmPassword = request.POST["confirmPassword"]

        try:
            uid = request.session["uid"]
        except (KeyError, TypeError):
            messages.warning(request, "You are not authenticated!!!")
            return redirect("login")

        if password == confirmPassword:
            # uid = request.session["uid"]
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset Successful!")
            return redirect("login")
        else:
            messages.warning(request, "Passwords do not match.")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/resetPassword.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "created_at"
    )

    context = {"orders": orders}
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # try:
    #     user_profile = get_object_or_404(UserProfile, user=request.user)
    # except UserProfile.DoesNotExist:
    #     user_profile = UserProfile.create(user=request.user, profile_picture=default_dp)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile has been updated.")
            return redirect("edit_profile")

    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "user_profile": user_profile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        new_password_again = request.POST["new_password_again"]

        user = Account.objects.get(username__exact=request.user.username)
        if new_password_again == new_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, "Password has been changed successfully.")
                return redirect("change_password")
            else:
                messages.warning(request, "Please provide valid current password")
                return redirect("change_password")
        else:
            messages.warning(request, "Passwords do not match.")
            return redirect("change_password")
    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def order_details(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        "order_detail": order_detail,
        "subtotal": subtotal,
        "order": order,
    }
    return render(request, "accounts/order_details.html", context)
