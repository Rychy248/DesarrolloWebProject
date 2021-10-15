from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from store.models import Product
import datetime
import json

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    
    # creatin the payment    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_id = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # moving the CartItem to the order product table
    cart_items = CartItem.objects.filter(user=request.user)
    
    for cart_item in cart_items:
        order_product = OrderProduct(
            order_id = order.id,
            payment = payment,
            user_id = request.user.id,
            product_id = cart_item.product_id,
            quantity = cart_item.quantity,
            product_price = cart_item.product.price,
            ordered = True,
        )
        order_product.save()

        cart_item = CartItem.objects.get(id=cart_item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variation.set(product_variation)
        order_product.save()
        
        product = Product.objects.get(id=cart_item.product_id)
        product.stock -= cart_item.quantity
        product.save()
        
    CartItem.objects.filter(user=request.user).delete()
    mail_subject = "Gracias por tu compra!"
    mail_body = render_to_string("orders/order_recieved_email.html",{
        'user':request.user,
        'order':order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,mail_body,to=[to_email])
    send_email.send()
    
    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }
    
    return JsonResponse(data)

def place_order(request, total=0,quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        #messages.success(request,'El carrito esta vacio')  
        return redirect('store')
    
    total = 0
    quantity = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (2 * total)/100 # Impuesto que se esta suponiendo es de 2%
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.impuesto = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            yr = int(datetime.date.today().strftime('%y'))    
            mt = int(datetime.date.today().strftime('%m'))    
            dt = int(datetime.date.today().strftime('%d'))    
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%M%T")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request, 'orders/payments.html',context)
        
        else:
            return redirect('store')
        
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for product in ordered_products:
            subtotal += product.product_price * product.quantity
        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
        }
        
        return render(request, "orders/order_complete.html",context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
        
    
    
    
    





