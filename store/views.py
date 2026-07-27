from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.db.models import Q, Sum
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import uuid
from django.conf import settings
import requests

from authapp import models as accounts_models
from store import models as store_models
from store.forms import ProductForm
from store.referrals import evaluate_referral_rewards, count_successful_referrals


def _is_frontdesk(user):
    return user.is_authenticated and (getattr(user, "role", None) == "ADMIN" or user.is_staff or user.is_superuser)


def frontdesk_required(view_func):
    def wrapped(request, *args, **kwargs):
        if not _is_frontdesk(request.user):
            messages.error(request, "You do not have access to the frontdesk tools.")
            return redirect("store:shop")
        return view_func(request, *args, **kwargs)

    return wrapped

def _get_cart_queryset(request, cart_id=None):
    cart_id = cart_id or request.session.get('cart_id')

    if request.user.is_authenticated:
        if cart_id:
            return store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).distinct()
        return store_models.Cart.objects.filter(user=request.user).distinct()

    if cart_id:
        return store_models.Cart.objects.filter(cart_id=cart_id).distinct()

    return store_models.Cart.objects.none()


# Create your views here.
def get_cart_count(request):
    cart_id = request.GET.get('cart_id') or request.session.get('cart_id')
    cart_items = _get_cart_queryset(request, cart_id)
    cart_sub_total = cart_items.aggregate(sub_total=Sum('sub_total'))['sub_total'] or Decimal('0.00')

    return JsonResponse({
        'total_cart_items': cart_items.count(),
        'cart_sub_total': f'{cart_sub_total:,.2f}',
        'total_price': f'{cart_sub_total:,.2f}',
    })


def shop(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.all()
    cart_items = _get_cart_queryset(request, request.session.get('cart_id'))
    in_cart_product_ids = set(cart_items.values_list('product_id', flat=True))
    event = (
        store_models.Event.objects.filter(is_active=True)
        .order_by("-created_at")
        .first()
    )
    event_tickets = []
    if event:
        event_tickets = event.tickets.filter(is_purchasable=True).order_by("price")

    context = {
        'categories': categories,
        'products': products,
        'category': None,
        'in_cart_product_ids': in_cart_product_ids,
        'event': event,
        'event_tickets': event_tickets,
    }

    return render(request, 'store/index.html', context)


def category_products(request, foo):
    category = store_models.Category.objects.get(slug=foo)
    products = store_models.Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
        'categories': store_models.Category.objects.all(),
    }

    return render(request, 'store/shop.html', context)


def product_detail(request, foo):
    product = store_models.Product.objects.get(slug=foo)

    context = {
        'product': product
    }

    return render(request, 'store/product_detail.html', context)


def AddToCart(request):
    product_id = request.GET.get('id')
    qty = request.GET.get('qty')
    cart_id = request.GET.get('cart_id') or request.session.get('cart_id')

    if not product_id or not qty or not cart_id:
        return JsonResponse({'error': f'Missing required parameters: product={product_id}, qty={qty}, cart_id={cart_id}'}, status=400)

    try:
        product = store_models.Product.objects.get(id=product_id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    try:
        qty_value = int(qty)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    if qty_value < 1:
        return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)

    request.session['cart_id'] = cart_id

    existing_cart_items = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    if not existing_cart_items:
        cart_item = store_models.Cart(
            product=product,
            price=product.price,
            qty=qty_value,
            sub_total=Decimal(product.price) * Decimal(qty_value),
            total=Decimal(product.price) * Decimal(qty_value),
            cart_id=cart_id,
            user=request.user if request.user.is_authenticated else None,
        )
        cart_item.save()
        message = f'Added {qty_value} of {product.name} to cart.'
    else:
        existing_cart_items.price = product.price
        existing_cart_items.qty = qty_value
        existing_cart_items.sub_total = Decimal(product.price) * Decimal(qty_value)
        existing_cart_items.total = Decimal(product.price) * Decimal(qty_value)
        existing_cart_items.user = request.user if request.user.is_authenticated else None
        existing_cart_items.cart_id = cart_id
        existing_cart_items.save()
        cart_item = existing_cart_items
        message = f'Updated {product.name} in cart to {qty_value}.'

    cart_items = _get_cart_queryset(request, cart_id)
    cart_sub_total = cart_items.aggregate(sub_total=Sum('sub_total'))['sub_total'] or Decimal('0.00')

    return JsonResponse({
        'message': message,
        'total_cart_items': cart_items.count(),
        'cart_sub_total': f'{cart_sub_total:,.2f}',
        'total_price': f'{cart_sub_total:,.2f}',
        'item_sub_total': f'{cart_item.sub_total:,.2f}',
    })


def cart(request):
    cart_id = request.session.get('cart_id')
    items = _get_cart_queryset(request, cart_id).order_by('-date')
    cart_sub_total = items.aggregate(sub_total=Sum('sub_total'))['sub_total'] or Decimal('0.00')
    total = items.aggregate(total=Sum('sub_total'))['total'] or Decimal('0.00')

    if not items.exists():
        messages.info(request, 'Your cart is empty.')

    context = {
        'items': items,
        'cart_sub_total': f'{cart_sub_total:,.2f}',
        'total': f'{total:,.2f}',
    }

    return render(request, 'store/shopping-cart.html', context)


def delete_cart_item(request):
    item_id = request.GET.get('item_id')
    cart_id = request.GET.get('cart_id') or request.session.get('cart_id')

    if not item_id:
        return JsonResponse({'error': 'Item not found'}, status=400)

    cart_items = _get_cart_queryset(request, cart_id)
    item = cart_items.filter(id=item_id).first()

    if not item:
        return JsonResponse({'error': 'Item not found'}, status=404)

    item.delete()
    remaining_items = _get_cart_queryset(request, cart_id)
    cart_sub_total = remaining_items.aggregate(sub_total=Sum('sub_total'))['sub_total'] or Decimal('0.00')

    return JsonResponse({
        'message': 'Item deleted',
        'total_cart_items': remaining_items.count(),
        'cart_sub_total': f'{cart_sub_total:,.2f}',
        'total_price': f'{cart_sub_total:,.2f}',
    })
    
    
@login_required(login_url='login')
def CreateOrder(request):
    if request.method == "POST":
        
        if "cart_id" in request.session:
            cart_id = request.session["cart_id"]
        else:
            cart_id = None
        
        items_cart = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else  Q(cart_id=cart_id))
        
        cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else  Q(cart_id=cart_id)).aggregate(sub_total = Sum("sub_total"))["sub_total"]

        pick_up_date = None
        pick_up_date_value = request.POST.get("pick_up_date")
        if pick_up_date_value:
            pick_up_date = parse_datetime(pick_up_date_value)
            if pick_up_date and timezone.is_naive(pick_up_date):
                pick_up_date = timezone.make_aware(pick_up_date)
                
        order = store_models.Order()
        
        order.customer = request.user if request.user.is_authenticated else None
        order.sub_total = cart_sub_total
        order.total = order.sub_total
        order.pick_up_date = pick_up_date
        
        order.save()
        for i in items_cart:
            store_models.OrderItem.objects.create(
                order=order,
                product=i.product,
                price=i.price,
                qty=i.qty,
                sub_total=i.sub_total,
            )
            
    
    return redirect("store:checkout", order.order_id)

@login_required(login_url='login')
def checkout(request, id):
    order = store_models.Order.objects.get(order_id=id)
    order_items = store_models.OrderItem.objects.filter(order=order)
    
    context = {
        "order":order,
        "order_items":order_items,
    }
    
    return render(request, "store/checkout.html", context)


@login_required(login_url='login')
def orders(request):
    orders = store_models.Order.objects.filter(customer=request.user).order_by("-date")
    context = {
        'orders':orders
    }
    
    return render(request, 'store/orders.html', context)

def order_detail(request, pk):
    order = store_models.Order.objects.get(order_id=pk)
    order_items = store_models.OrderItem.objects.filter(order=order)
    
    context = {
        "order":order,
        "order_items":order_items,
    }
    
    return render(request, 'store/order_detail.html', context)


@frontdesk_required
def frontdesk_orders(request):
    orders = store_models.Order.objects.select_related("customer").prefetch_related("orderitem_set").order_by("-date")
    context = {
        "orders": orders,
        "pending_count": orders.filter(order_status="Pending").count(),
        "processing_count": orders.filter(order_status="Processing").count(),
    }
    return render(request, "store/frontdesk_orders.html", context)


@frontdesk_required
@require_POST
def confirm_order(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)

    if order.order_status == "Delivered":
        messages.info(request, f"Order #{order.order_id} is already delivered.")
        return redirect("store:frontdesk_orders")

    order.order_status = "Processing"
    if order.payment_status == "Processing":
        order.payment_status = "Paid"
    if not order.payment_method:
        order.payment_method = "Cash"
    order.save(update_fields=["order_status", "payment_status", "payment_method"])

    messages.success(request, f"Order #{order.order_id} confirmed for the kitchen.")
    return redirect("store:frontdesk_orders")


@frontdesk_required
@require_POST
def mark_order_delivered(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)

    if order.order_status == "Delivered":
        return JsonResponse({
            "success": False,
            "message": f"Order #{order.order_id} is already delivered.",
            "order_status": order.order_status,
        }, status=400)

    order.order_status = "Delivered"
    if order.payment_status == "Processing":
        order.payment_status = "Paid"
    if not order.payment_method:
        order.payment_method = "Cash"
    order.save(update_fields=["order_status", "payment_status", "payment_method"])

    return JsonResponse({
        "success": True,
        "message": f"Order #{order.order_id} marked as delivered.",
        "order_id": str(order.order_id),
        "order_status": order.order_status,
    })

@frontdesk_required
def frontdesk_search_orders(request):
    q = request.GET.get("q", "")
    orders = (
        store_models.Order.objects.select_related("customer")
        .filter(
            Q(order_id__icontains=q)
            | Q(customer__username__icontains=q)
            | Q(customer__email__icontains=q)
            | Q(order_status__icontains=q)
            | Q(payment_status__icontains=q)
        )
        .order_by("-date")
    )

    payload = []
    for order in orders:
        payload.append({
            "order_id": order.order_id,
            "customer": order.customer.username if order.customer else "Guest",
            "email": order.customer.email if order.customer else "",
            "total": f"{order.total:,.2f}",
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "payment_method": order.payment_method or "-",
            "date": order.date.strftime("%b %d, %Y %I:%M %p"),
            "pick_up_date": order.pick_up_date.strftime("%b %d, %Y %I:%M %p") if order.pick_up_date else "-",
            "item_count": order.order_items().count(),
            "detail_url": reverse("store:order_detail", args=[order.order_id]),
            "confirm_url": reverse("store:confirm_order", args=[order.order_id]),
            "delivered_url": reverse("store:mark_order_delivered", args=[order.order_id]),
        })

    return JsonResponse({"orders": payload})


@frontdesk_required
def frontdesk_products(request):
    products = store_models.Product.objects.select_related("category").order_by("-id")
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "total_products": products.count(),
    }
    return render(request, "store/frontdesk_products.html", context)


@frontdesk_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect("store:frontdesk_products")
    else:
        form = ProductForm()

    return render(request, "store/frontdesk_product_form.html", {
        "form": form,
        "page_title": "Add Product",
        "submit_label": "Create Product",
    })


@frontdesk_required
def edit_product(request, product_id):
    product = get_object_or_404(store_models.Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("store:frontdesk_products")
    else:
        form = ProductForm(instance=product)

    return render(request, "store/frontdesk_product_form.html", {
        "form": form,
        "product": product,
        "page_title": f"Edit {product.name}",
        "submit_label": "Save Changes",
    })

@login_required(login_url='accounts:login')
def FlutterWavePayment(request, order_id):
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        
        tx_ref = str(uuid.uuid4())
        
        url = "https://api.flutterwave.com/v3/payments"
        
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "tx_ref": tx_ref,
            "amount": str(order.total),
            "currency": "NGN",
            "redirect_url": f"http://127.0.0.1:8800/verify-payment/{order_id}",
            "customer":{
                'email': request.user.email,
                'name': request.user.username,
            },
            'customizations':{
                "title": f"Payment for Order with ID {order_id}"
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        result = response.json()
        if result.get('status') == 'success':
            payment_link = result['data']['link']
            print(payment_link)
            return redirect(payment_link)
        else:
            return render(request, 'store/checkout.html', {'error': result.get('message', 'Payment initiation failed.')})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, 'store/checkout.html', {'error': 'An unexpected error occurred. Please try again later.'})
         
@login_required(login_url='login')
def PaymentCallback(request, order_id):
    status = request.GET.get('status')
    
    order = store_models.Order.objects.get(order_id=order_id)
    transaction_id = request.GET.get('transaction_id')
    
    print(f"Payment status: {status}, Transaction ID: {transaction_id}")
    # subtract order item qty from product qty from the database if payment is successful
    items = store_models.OrderItem.objects.filter(order=order)    
    
    if transaction_id and order.payment_status == "Processing":
        if status in ['successful', 'completed']:
            order.payment_status = 'Paid'
            order.payment_method = 'Flutterwave'
            order.payment_id = transaction_id
            order.save()
            for item in items:
                product = store_models.Product.objects.get(id=item.product.id)
                product.stock -= item.qty
                product.save()
            
            # html_message = render_to_string(
            #     'email/order_confirmation.html',
            #     {'order': order, 'items': items}
            # )
            # plain_message = strip_tags(html_message)
            # send_mail(
            #     subject='Order Confirmation',
            #     message=plain_message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[request.user.email],
            #     html_message=html_message
            # )
            # clear the cart after successful payment
            if "cart_id" in request.session:
                cart_id = request.session["cart_id"]
                store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).delete()
                del request.session["cart_id"]
                
            messages.success(request, "Payment successful. Your order has been placed.")
            return redirect("store:shop")
    
    order.payment_status = 'Failed'
    order.save()
    messages.error(request, "Payment failed. Please try again.")
    return redirect("store:checkout", order_id)


# --- Event tickets ---

@login_required(login_url='login')
def event_tickets(request):
    event = (
        store_models.Event.objects.filter(is_active=True)
        .prefetch_related("tickets")
        .order_by("-created_at")
        .first()
    )
    tickets = []
    if event:
        tickets = event.tickets.filter(is_purchasable=True)

    referral_stats = None
    if request.user.is_authenticated and event and request.user.referral_code:
        count = count_successful_referrals(event, request.user.referral_code)
        rewards = store_models.ReferralReward.objects.filter(
            referrer=request.user, event=event
        )
        referral_stats = {
            "code": request.user.referral_code,
            "count": count,
            "rewards": rewards,
        }

    context = {
        "event": event,
        "tickets": tickets,
        "referral_stats": referral_stats,
    }
    return render(request, "store/event_tickets.html", context)


@login_required(login_url='login')
@require_POST
def create_event_order(request):
    ticket_id = request.POST.get("ticket_id")
    qty_raw = request.POST.get("qty", "1")
    referred_by_code = (request.POST.get("referred_by_code") or "").strip().upper() or None

    ticket = get_object_or_404(
        store_models.EventTicket,
        id=ticket_id,
        is_purchasable=True,
        event__is_active=True,
    )

    try:
        qty = max(1, int(qty_raw))
    except (TypeError, ValueError):
        messages.error(request, "Invalid quantity.")
        return redirect("store:event_tickets")

    if referred_by_code:
        referrer = accounts_models.User.objects.filter(
            referral_code__iexact=referred_by_code
        ).first()
        if not referrer:
            messages.error(request, "Invalid referral code.")
            return redirect("store:event_tickets")
        if referrer.id == request.user.id:
            messages.error(request, "You cannot use your own referral code.")
            return redirect("store:event_tickets")

    unit_price = ticket.price
    total = Decimal(unit_price) * Decimal(qty)

    order = store_models.EventOrder.objects.create(
        customer=request.user,
        event=ticket.event,
        ticket=ticket,
        qty=qty,
        unit_price=unit_price,
        total=total,
        referred_by_code=referred_by_code,
        payment_status="Processing",
        order_status="Pending",
    )

    return redirect("store:event_checkout", order.order_id)


@login_required(login_url='login')
def event_checkout(request, order_id):
    order = get_object_or_404(
        store_models.EventOrder.objects.select_related("ticket", "event", "customer"),
        order_id=order_id,
        customer=request.user,
    )
    return render(request, "store/event_checkout.html", {"order": order})


@login_required(login_url='login')
def event_orders(request):
    orders = (
        store_models.EventOrder.objects.filter(customer=request.user)
        .select_related("ticket", "event")
        .order_by("-date")
    )
    rewards = store_models.ReferralReward.objects.filter(
        referrer=request.user
    ).select_related("event", "free_ticket_order")
    return render(
        request,
        "store/event_orders.html",
        {"orders": orders, "rewards": rewards},
    )


@login_required(login_url='login')
def FlutterWaveEventPayment(request, order_id):
    try:
        order = get_object_or_404(
            store_models.EventOrder, order_id=order_id, customer=request.user
        )
        if order.payment_status == "Paid":
            messages.info(request, "This ticket order is already paid.")
            return redirect("store:event_orders")

        tx_ref = str(uuid.uuid4())
        url = "https://api.flutterwave.com/v3/payments"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "tx_ref": tx_ref,
            "amount": str(order.total),
            "currency": "NGN",
            "redirect_url": request.build_absolute_uri(
                reverse("store:event_payment_callback", args=[order.order_id])
            ),
            "customer": {
                "email": request.user.email,
                "name": request.user.username,
            },
            "customizations": {
                "title": f"Event ticket — {order.ticket.name} (#{order.order_id})",
            },
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        if result.get("status") == "success":
            return redirect(result["data"]["link"])

        messages.error(request, result.get("message", "Payment initiation failed."))
        return redirect("store:event_checkout", order.order_id)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("store:event_checkout", order_id)


@login_required(login_url='login')
def EventPaymentCallback(request, order_id):
    status = request.GET.get("status")
    transaction_id = request.GET.get("transaction_id")
    order = get_object_or_404(
        store_models.EventOrder, order_id=order_id, customer=request.user
    )

    if transaction_id and order.payment_status == "Processing":
        if status in ["successful", "completed"]:
            order.payment_status = "Paid"
            order.payment_method = "Flutterwave"
            order.payment_id = transaction_id
            order.order_status = "Processing"
            order.save(
                update_fields=[
                    "payment_status",
                    "payment_method",
                    "payment_id",
                    "order_status",
                ]
            )

            if order.ticket.stock > 0:
                order.ticket.stock = max(0, order.ticket.stock - order.qty)
                order.ticket.save(update_fields=["stock"])

            evaluate_referral_rewards(order)

            messages.success(
                request,
                "Payment successful. Your event ticket order is confirmed.",
            )
            return redirect("store:event_orders")

    order.payment_status = "Failed"
    order.save(update_fields=["payment_status"])
    messages.error(request, "Payment failed. Please try again.")
    return redirect("store:event_checkout", order.order_id)


@frontdesk_required
def frontdesk_event_orders(request):
    orders = (
        store_models.EventOrder.objects.select_related("customer", "ticket", "event")
        .order_by("-date")
    )
    rewards = (
        store_models.ReferralReward.objects.select_related(
            "referrer", "event", "free_ticket_order"
        )
        .order_by("-date")
    )
    return render(
        request,
        "store/frontdesk_event_orders.html",
        {"orders": orders, "rewards": rewards},
    )


@frontdesk_required
@require_POST
def fulfill_referral_reward(request, reward_id):
    reward = get_object_or_404(store_models.ReferralReward, id=reward_id)
    reward.status = "Fulfilled"
    reward.save(update_fields=["status"])
    if reward.free_ticket_order and reward.free_ticket_order.order_status != "Delivered":
        reward.free_ticket_order.order_status = "Delivered"
        reward.free_ticket_order.save(update_fields=["order_status"])
    messages.success(
        request,
        f"Marked reward for {reward.referrer.email} as fulfilled.",
    )
    return redirect("store:frontdesk_event_orders")


