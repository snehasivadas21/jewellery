from django.shortcuts import render,redirect,get_object_or_404
from utils.decorators import admin_required
from django.contrib.auth.decorators import login_required
from .models import Coupon,UserCoupon
from cart.models import Cart, CartItem
from .forms import CouponForm
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
import string
import random

# Create your views here.
@admin_required
def list_coupon(request):
    coupons=Coupon.objects.all()
    return render(request,'admin_side/list_coupon.html',{'coupons':coupons})

@admin_required
def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-coupon')
    else:
        form = CouponForm()
    return render(request,'admin_side/create_edit_coupon.html',{'form':form})

@admin_required
def generate_coupon_code(request):
    if request.method == "GET":
        length = 8
        characters = string.ascii_uppercase + string.digits
        coupon_code=''.join(random.choice(characters) for _ in range(length))
        return JsonResponse({'coupon_code':coupon_code})
    
@admin_required
def edit_coupon(request,pk):
    coupon = get_object_or_404(Coupon,pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('list-coupon')
    else:
        form =CouponForm(instance=coupon)
    return render(request,'admin_side/create_edit_coupon.html',{'form':form})

@admin_required
def coupon_status(request,pk):
    coupon = get_object_or_404(Coupon,pk=pk)
    if request.method == 'POST':
        coupon.status = not coupon.status
        coupon.save()
        status_message ='activated' if coupon.status else 'deactivated'
        messages.success(request,f'Coupon successfully {status_message}.')
        return redirect('list-coupon')
    
# user side coupon funtions

@require_POST 
@login_required
def apply_coupon(request):
    coupon_code = request.POST.get('coupon_code')

    if not coupon_code:
        return JsonResponse({'success':False,'message':'Please enter a coupon code.'})
    
    try:
        coupon = Coupon.objects.get(coupon_code=coupon_code,status=True)
    except Coupon.DoesNotExist:
        return JsonResponse({'success':False,'message':'Invalid coupon code.'})
    if coupon.expiry_date < timezone.now().date():
        return JsonResponse({'success':False,'message':'This coupon has expired.'})
    try:
        cart=Cart.objects.get(user=request.user)
        selected_items_ids=request.POST.getlist('selected_items[]')
        cart_items = CartItem.objects.filter(cart=cart,is_active=True,id__in=selected_items_ids)
        cart_total =sum(item.sub_total() for item in cart_items)
    except Cart.DoesNotExist:
        return JsonResponse({'success':False,'message':'Your cart is empty.'})

    if cart_total < coupon.minimum_amount:
        return JsonResponse({
            'success':False,
            'message':f'Your cart total must be at least ₹{coupon.minimum_amount} to use this coupon.'
        })    
    discount_amount =(cart_total * coupon.discount) // 100

    if coupon.maximum_amount > 0:
        discount_amount = min(discount_amount,coupon.maximum_amount)

    final_total = cart_total - discount_amount

    UserCoupon.objects.create(user=request.user,coupon=coupon,used = True, used_at=timezone.now())
    request.session['applied_coupon'] = coupon.id

    return JsonResponse({
        'success':True,
        'message':'Coupon applied successfully',
        'cart_total':float(cart_total),
        'discount_amount':float(discount_amount),
        'final_total':float(final_total)
    }) 

@require_POST
@login_required
def remove_coupon(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart.coupon = None
        cart.save()
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        response_data={
            'success':True,
            'message':'Coupon removed successfully.'
        }
    except Cart.DoesNotExist:
        response_data = {
            'success':False,
            'message':'Cart not found.'
        }
    return JsonResponse(response_data)             
    
        


       





