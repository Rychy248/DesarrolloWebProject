from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ProductGallery, ReviewRating
from orders.models import OrderProduct
from category.models import Category
from carts.models import CartItem
from carts.views import __cart_id
from .forms import ReviewForm

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('-product_name')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-product_name')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    
    context = {
        'products':paged_products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    #dos rayas para abaja, indican que se quiere compara un valor del campo
    #tablaName__tablaCampo
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=__cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None
        
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'order_product':order_product,
        'reviews':reviews,
        'product_gallery':product_gallery,
    }    
    
    return render(request, 'store/product_detail.html',context)
    
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-product_name').filter(
                Q(description__icontains=keyword) |
                Q(product_name__icontains=keyword)
            )
            product_count = products.count()
        else:
            products = []
            product_count = 0
        
    context = {
        'products':products,
        'product_count':product_count,
    }
    
    return render(request,'store/store.html', context)

def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Muchas gracias, tu comentario ha sido actualizado')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating(
                    subject=form.cleaned_data['subject'],
                    rating=form.cleaned_data['rating'],
                    review=form.cleaned_data['review'],
                    ip=request.META.get('REMOTE_ADDR'),
                    product_id=product_id,
                    user_id=request.user.id
                )
                data.save()
                messages.success(request, 'Muchas gracias, tu comentario fue posteado exitosamente')
                return redirect(url)