from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.
def __cart_id(request):
    cart_id = request.session.session_key
    
    if not cart_id:
        cart_id = request.session.create()
    
    return cart_id

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    
    current_user = request.user
    
    if current_user.is_authenticated:    
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except :
                    pass
                
        is_cart_item_exist = CartItem.objects.filter(product=product,user=current_user).exists()
        
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    # asterisco da una coleccion
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                user = current_user,
                )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            
        return redirect('cart')
    else:
            
        product_variation = []
        
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except :
                    print("Un error en obtener los datos existentes")
        try:
            cart = Cart.objects.get(cart_id=__cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=__cart_id(request)
                )
        cart.save()
        
        is_cart_item_exist = CartItem.objects.filter(product=product,cart=cart).exists()
        
        if is_cart_item_exist:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    # asterisco da una coleccion
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart = cart,
                )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else: 
            cart = Cart.objects.get(cart_id=__cart_id(request))            
            cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass    
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=__cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
        
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_item=None):
    impuesto = 0
    grand_total = 0
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=__cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        
        total_price = 0
        total_products_quantity = 0
        
        for cart_item in cart_items:
            total_price += (cart_item.product.price*cart_item.quantity)
            total_products_quantity += cart_item.quantity
        
        impuesto = (2*total_price)/100 #suponiendo que el impuesto es de 2 porciento
        grand_total = total_price + impuesto
        
    except ObjectDoesNotExist:
        total_price = 0
        total_products_quantity = 0
        cart_items = 0
    
    context = {
        'total_price': total_price,
        'total_products_quantity': total_products_quantity,
        'cart_items': cart_items,
        'impuesto': impuesto,
        'grand_total': grand_total,
    }
    
    return render(request, "store/cart.html",context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_item=None):
    impuesto = 0
    grand_total = 0
    
    try: 
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id=__cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        
            
        total_price = 0
        total_products_quantity = 0
        
        for cart_item in cart_items:
            total_price += (cart_item.product.price*cart_item.quantity)
            total_products_quantity += cart_item.quantity
        
        impuesto = (2*total_price)/100 #suponiendo que el impuesto es de 2 porciento
        grand_total = total_price + impuesto
        
    except ObjectDoesNotExist:
        total_price = 0
        total_products_quantity = 0
        cart_items = 0
    
    context = {
        'total_price': total_price,
        'total_products_quantity': total_products_quantity,
        'cart_items': cart_items,
        'impuesto': impuesto,
        'grand_total': grand_total,
    }
    
    return render(request, 'store/checkout.html', context)