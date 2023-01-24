from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification Email, User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

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
            auth.login(request, user)
            messages.success(request, "Logged in successfully")
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
    return render(request, "accounts/dashboard.html")


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
