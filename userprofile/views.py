from django.shortcuts import render,redirect
from .models import UserAddress
from django.shortcuts import render,get_object_or_404
from.forms import UserProfileForm,UserAddressForm
from django.contrib import messages
from order.models import OrderMain,OrderSub,ReturnRequest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from decimal import Decimal
from .models import Wishlist,Product_Variant
import json
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
@login_required(login_url='/login/')
def user_profile(request):
    return render(request,'user_side/user_profile.html')

@login_required(login_url='/login/')
def user_address(request):
    user_addresses=UserAddress.objects.filter(user=request.user).order_by('-status','id')
    paginator=Paginator(user_addresses,2)
    page_number = request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    context={'page_obj':page_obj}

    return render(request,'user_side/user_address.html',context)

def add_or_edit_address(request,address_id=None):
    if address_id:
        address=get_object_or_404(UserAddress,id=address_id,user=request.user)
    else:
        address=None

    if request.method=='POST':
        form=UserAddressForm(request.POST,instance=address)
        if form.is_valid():
            form.instance.user=request.user
            form.save()
            return redirect('user-address')
    else:
        form=UserAddressForm(instance=address)

    context={'form':form,
             'is_edit':address_id is not None,
             'address_id':address_id}
    return render(request,'user_side/useradd_address.html',context)

@login_required
def delete_address(request,address_id):
    address=get_object_or_404(UserAddress,id=address_id,user=request.user)
    address.delete()
    messages.success(request,'Address deleted successfully.')
    return redirect('user-address')

def user_orders_view(request):
    user=request.user
    orders=OrderMain.objects.filter(user=user).prefetch_related('ordersub_set__variant__product','address').order_by('-id')
    status_list=["Pendings","Awaiting payment","Confirmed","Shipped"]

    paginator=Paginator(orders,3)
    page=request.GET.get('page')
    
    try:
        orders_page=paginator.page(page)
    except PageNotAnInteger:
        orders_page=paginator.page(1)
    except EmptyPage:
        orders_page=paginator.page(paginator.num_pages)

    for order in orders_page:
        order.has_active_items=order.ordersub_set.filter(is_active=True).exists()
        print(f"Order ID:{order.id},Status:{order.order_status},Has Active Items:{order.has_active_items}")
        for item in order.ordersub_set.all():
            item.return_status=ReturnRequest.objects.filter(order_sub=item).first()
    return render(request,'user_side/order_list.html',{'orders':orders_page,'status_list':status_list})

@login_required
@require_POST        
def cancel_order(request,order_id):
    order=get_object_or_404(OrderMain,id=order_id,user=request.user)

    if order.order_status not in ['Pending ','Confirmed','Shipped']:
        messages.error(request,'Order cannot be cancelled at this stage.')
        return redirect('order-list')
    with transaction.atomic():
        refund_amount=Decimal('0.00')
        active_items=order.ordersub_set.filter(is_active=True)

        for item in active_items:
            item_total_cost=Decimal(str(item.total_cost()))
            order_total_amount=Decimal(str(order.total_amount))
            order_discount_amout=Decimal(str(order.discount_amount))

            item_discount_amount=(order_discount_amout*item_total_cost)/order_total_amount
            item_refund_amount=item_total_cost - item_discount_amount

            refund_amount +=item_refund_amount
            item.is_active=False
            item.status='Calceled'
            item.save()
        order.order_status='Cancaled'
        order.is_active=False
        order.save()

    return redirect('order-list')

@login_required
@require_POST
def cancel_order_item(request):
    order_sub_id = request.POST.get('order_sub_id')
    order_item = get_object_or_404(OrderSub, id=order_sub_id, user=request.user)
    main_order = order_item.main_order

    if not order_item.is_active:
        messages.error(request, 'Order item is already canceled.')
        return redirect('order-list')

    if main_order.order_status not in ['Pending', 'Confirmed', 'Shipped']:
        messages.error(request, 'Order cannot be canceled at this stage.')
        return redirect('order-list')
    
    order_item.is_active = False
    order_item.status='Canceled'
    order_item.save()

    all_canceled = not main_order.ordersub_set.filter(is_active=True).exists()
    
    if all_canceled:
        main_order.order_status = 'Canceled'
        main_order.save()

    messages.success(request, 'Order item canceled successfully.')
    return redirect('order-list')
    

def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('user-profile') 
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user_side/password_change_form.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user-profile') 
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'user_side/edit_profile.html', {'form': form})



                         



        
                


