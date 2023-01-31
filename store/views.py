from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
import random
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from store.forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    random_price_discount = random.randint(1, 40)

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        # categories1 = Category.objects.all()
        products = Product.objects.filter(
            category=categories, is_available=True
        ).order_by("price")
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by("price")
        # categories1 = Category.objects.all()
        products_count = products.count()
    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)

    context = {
        "products": paged_products,
        "products_count": products_count,
        "random_price_discount": random_price_discount
        # "categories": categories1,
    }
    return render(request, "store.html", context)


def product_detail(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            ordered_products = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id
            ).exists()
        except OrderProduct.DoesNotExist:
            ordered_products = None
    else:
        ordered_products = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    review_count = reviews.count()
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    context = {
        "single_product": single_product,
        "in_cart": in_cart,
        "ordered_products": ordered_products,
        "reviews": reviews,
        "review_count": review_count,
        "product_gallery": product_gallery,
    }
    return render(request, "product_detail.html", context)


def search(request):
    context = {"products_count": 0}
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.filter(
                Q(desc__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            products_count = products.count()
            context = {
                "products": products,
                "products_count": products_count,
                "keyword": keyword,
            }
    return render(request, "store.html", context)


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.review = form.cleaned_data["review"]
                data.rating = form.cleaned_data["rating"]
                data.subject = form.cleaned_data["subject"]
                data.product_id = product_id
                data.user_id = request.user.id
                data.ip = request.META.get("REMOTE_ADDR")
                data.save()
                messages.success(request, "Thank you. Your review has been submitted")
            return redirect(url)
