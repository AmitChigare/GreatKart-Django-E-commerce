from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category
import random
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q

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
    context = {
        "single_product": single_product,
        "in_cart": in_cart,
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
