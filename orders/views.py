from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from accounts.models import Account
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import razorpay
from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    try:
        razorpay_client.payment.fetch(body['transID'])

        # Store transaction details inside Payment model
        payment = Payment(
            user = request.user,
            payment_id = body['transID'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status = body['status'],
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct.objects.create(
                order_id=order.id,
                payment=payment,
                user_id=request.user.id,
                product_id=item.product_id,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True
            )

            # Add variations
            orderproduct.variations.set(item.variations.all())
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            if(product.stock<1):
                product.is_available=False
            product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order recieved email to customer
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        # Send order number and transaction id back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (15 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            if current_user.first_name=="":
                current_user.first_name=data.first_name
            data.last_name = form.cleaned_data['last_name']
            if current_user.last_name=="":
                current_user.last_name=data.last_name
            data.phone = form.cleaned_data['phone']
            if current_user.phone_number=="":
                current_user.phone_number=data.phone
            data.email = form.cleaned_data['email']
            if current_user.email=="":
                current_user.email=data.email
            data.address_line_1 = form.cleaned_data['address_line_1']
            if current_user.address_line_1=="":
                current_user.address_line_1=data.address_line_1
            data.address_line_2 = form.cleaned_data['address_line_2']
            if current_user.address_line_2=="":
                current_user.address_line_2=data.address_line_2
            data.state = form.cleaned_data['state']
            if current_user.state==None:
                current_user.state=data.state
            data.city = form.cleaned_data['city']
            if current_user.city==None:
                current_user.city=data.city
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            current_user.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            # **Create Razorpay Order**
            razorpay_order = razorpay_client.order.create({
                "amount": int(grand_total * 100),  # Amount in paisa (100 INR = 10000)
                "currency": "INR",
                "payment_capture": "1"  # Auto-capture payment
            })

            # Store order_id in session to verify later
            request.session['razorpay_order_id'] = razorpay_order['id']
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razorpay_order_id': razorpay_order['id'],  # Pass to frontend
                'razorpay_key': settings.RAZORPAY_KEY_ID,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html')
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    
def return_order(request):
    pass