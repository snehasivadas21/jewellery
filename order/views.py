from userprofile.models import UserAddress 
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import OrderMain, OrderSub ,ReturnRequest ,OrderAddress
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse ,HttpResponseRedirect
from django.utils.crypto import get_random_string
from utils.decorators import admin_required
from django.core.paginator import Paginator
from cart.models import CartItem, Cart
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
from decimal import Decimal
import uuid

# Create your views here.

@admin_required
def admin_order_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'Show all')
    items_per_page = request.GET.get('items_per_page', 10)


    orders = OrderMain.objects.all().order_by('-id')
    if search_query:
        orders = orders.filter(order_id__icontains=search_query)
    if status_filter != 'Show all':
        orders = orders.filter(order_status=status_filter)


    paginator = Paginator(orders, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'items_per_page': items_per_page,
        'ORDER_STATUS_CHOICES': OrderMain.ORDER_STATUS_CHOICES,
    }
    return render(request, 'admin_side/order_list.html', context)


@admin_required
def admin_orders_details(request, oid):
    order = get_object_or_404(OrderMain, pk=oid)
    order_items = OrderSub.objects.filter(main_order=order)
    return render(request, 'admin_side/order_details.html', {'orders': order, 'order_sub': order_items})


@admin_required
def change_order_status(request, order_id):
    order = get_object_or_404(OrderMain, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('order_status')

        current_status = order.order_status
        invalid_transitions = {
            'Awaiting payment': ['Pending'],
            'Confirmed': ['Pending', 'Awaiting payment'],
            'Shipped': ['Confirmed', 'Awaiting payment', 'Pending'],
            'Delivered': ['Shipped', 'Confirmed', 'Awaiting payment', 'Pending'],
            'Canceled': [status for status, _ in OrderMain.ORDER_STATUS_CHOICES] ,
            'Returned': [status for status, _ in OrderMain.ORDER_STATUS_CHOICES]
        }

        if new_status == 'Returned':
            messages.error(request, 'Order status cannot be changed to Returned directly by the admin.')
        elif current_status in invalid_transitions and new_status in invalid_transitions[current_status]:
            messages.error(request, f'Cannot change status from {current_status} to {new_status}.')
        
    return redirect('admin-orders-details', oid=order.id)


#user side order fuctions

def generate_unique_order_id():
    return str(uuid.uuid4())


@csrf_exempt
def order_placed(request):
    if request.method == "POST":
        try:
            user = request.user
            cart_item_ids = request.POST.get('cart_item_ids', '')
            selected_address_id = request.POST.get('selected_address')
            payment_method = request.POST.get('payment_method')

            if not selected_address_id:
              messages.error(request, "No address selected. Please choose a delivery address.")
              return redirect('cart')  # Redirect to the cart if the address is missing.


            cart_item_ids = cart_item_ids.split(',')
            cart_items = CartItem.objects.filter(id__in=cart_item_ids, cart__user=user)
            if not cart_items.exists():
                messages.error(request, "No valid items found. Please try again.")
                return redirect(f'{reverse("checkout")}?selected_address={selected_address_id}')

            for item in cart_items:
                if item.quantity > item.variant.variant_stock:
                    messages.error(request, f"Insufficient stock for {item.product.product_name}.")
                    return redirect(f'{reverse("checkout")}?selected_address={selected_address_id}')

                if not item.product.is_active or not item.variant.variant_status:
                    messages.error(request, f"{item.product.product_name} is no longer available.")
                    return redirect(f'{reverse("checkout")}?selected_address={selected_address_id}')

            user_address = UserAddress.objects.get(id=selected_address_id)

            order_address = OrderAddress.objects.create(
                name=user_address.name,
                phone_number=user_address.phone_number,
                house_name=user_address.house_name,
                street_name=user_address.street_name,
                district=user_address.district,
                state=user_address.state,
                country=user_address.country,
                pin_number=user_address.pin_number
            )

            total_amount = sum(item.sub_total() for item in cart_items)
            final_amount = total_amount

            if payment_method == 'cash_on_delivery':
                if final_amount > 500000:
                    messages.error(request, "Cash on Delivery is not available for orders above ₹500000.")
                    return redirect(f'{reverse("checkout")}?selected_address={selected_address_id}')

                order = OrderMain.objects.create(
                    user=user,
                    address=order_address,
                    total_amount=total_amount,
                    final_amount=final_amount,
                    payment_option=payment_method,
                    order_id=generate_unique_order_id(),
                    order_status='Confirmed',
                    payment_status=False,
                )

                for item in cart_items:
                    OrderSub.objects.create(
                        user=user,
                        main_order=order,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=item.product.offer_price,
                    )
                    variant = item.variant
                    variant.variant_stock -= item.quantity
                    variant.save()
                    item.delete()

                return redirect('order-confirmation', order_id=order.id)

        except UserAddress.DoesNotExist:
            messages.error(request, "Selected address does not exist.")
            return HttpResponseRedirect(reverse('checkout'))
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return HttpResponseRedirect(reverse('checkout'))
    else:
        return HttpResponseRedirect(reverse('checkout'))

def order_failure(request, order_id):
    print('you fail')
    order = get_object_or_404(OrderMain, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'user_side/order_failure.html', context)    


def order_confirmation(request, order_id):
    order = get_object_or_404(OrderMain, id=order_id)
    future_date_time = timezone.now() + timedelta(days=5)
    estimated_delivery_date = future_date_time.strftime("Arriving By %d %a %B %Y")
    return render(request, 'user_side/order_placed.html', {'order': order ,'estimated_delivery_date': estimated_delivery_date})




