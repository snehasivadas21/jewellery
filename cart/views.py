from django.shortcuts import render ,redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from product.models import Products, Product_Variant ,Product_variant_images
from django.http import JsonResponse
from django.contrib import messages
from userprofile.models import UserAddress
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
from .context_processors import cart_and_wishlist_counts
import re

# Create your views here.

@login_required(login_url='/login/')
def cart_view(request):
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=user_cart, is_active=True).order_by('-cart__updated_at')
    cart_total = sum(item.sub_total() for item in cart_items)

    for item in cart_items:
        item.variant_image = Product_variant_images.objects.filter(product_variant=item.variant).first()

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'user_side/cart_view.html', context)

def update_counts(request):
    counts = cart_and_wishlist_counts(request)
    return JsonResponse(counts)

@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))  
        variant = get_object_or_404(Product_Variant, id=variant_id)
        product = variant.product

        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )
                   
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})


def remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart-view') 


@csrf_exempt
@login_required
def update_cart_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('quantity')
        selected_items = request.POST.getlist('selected_items[]')
        
        cart_total = Decimal('0')
        item_sub_total = Decimal('0')
        
        if item_id != 'dummy' and new_quantity:
            try:
                new_quantity = int(new_quantity)
                if new_quantity < 1 or new_quantity > 5:
                    return JsonResponse({'success': False, 'error': 'Quantity must be between 1 and 5'})
                
                cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
                if new_quantity > cart_item.variant.variant_stock:
                    return JsonResponse({'success': False, 'error': 'Quantity exceeds available stock'})
                
                cart_item.quantity = new_quantity
                cart_item.save()
                item_sub_total = cart_item.sub_total()
            except CartItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Cart item not found'})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid quantity'})
        
        selected_cart_items = CartItem.objects.filter(cart__user=request.user, id__in=selected_items, is_active=True)
        cart_total = sum(item.sub_total() for item in selected_cart_items)
        
        
        
        return JsonResponse({
            'success': True,
            'cart_total': float(cart_total),
            'item_sub_total': float(item_sub_total),
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def checkout(request):
    user = request.user
    cart_item_ids = request.GET.get('cart_items', '')
    
    if not cart_item_ids:
        messages.error(request, "No items selected.Please select items before proceeding to checkout.")
        return redirect('cart-view') 
    

    cart_item_ids = cart_item_ids.split(',')
    cart_items = CartItem.objects.filter(id__in=cart_item_ids, cart__user=user)
    
    if not cart_items.exists():
        messages.error(request, "No valid items found in cart. Please try again.")
        return redirect('cart-view')  
    
    for item in cart_items:
        if item.quantity > item.variant.variant_stock:
            messages.error(request, f"Insufficient stock for {item.product.product_name}.")
            return redirect('cart-view')
        if not item.product.is_active or not item.variant.variant_status:
            messages.error(request, f"{item.product.product_name} is no longer available.")
            return redirect('cart-view')

    user_addresses = UserAddress.objects.filter(user=user)
    

    for item in cart_items:
        item.variant_image = Product_variant_images.objects.filter(product_variant=item.variant).first()


    cart_total = sum(item.sub_total() for item in cart_items)
    discount_amount = Decimal('0.00')

    context = {
        'user_addresses': user_addresses,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'discount_amount': discount_amount,
        'cart_item_ids': ','.join(map(str, cart_items.values_list('id', flat=True))),
    }
    return render(request, 'user_side/checkout.html', context)



@login_required
def check_cart_status(request):
    variant_id = request.GET.get('variant_id')
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    is_in_cart = CartItem.objects.filter(cart=cart, variant_id=variant_id, is_active=True).exists()
    
    return JsonResponse({'is_in_cart': is_in_cart})


def add_address(request):
    if request.method == 'POST':

        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        is_default = request.POST.get('is_default') == 'on'

        new_address =UserAddress(
            user=request.user,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )

        try:
            new_address.save()
            messages.success(request, 'New address added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding new address: {str(e)}')

    return redirect(reverse('checkout'))



@login_required
def add_address(request):
    # Process the form data
    new_address = UserAddress(
        user=request.user,
        name=request.POST['name'],
        phone_number=request.POST['phone_number'],
        house_name=request.POST['house_name'],
        street_name=request.POST['street_name'],
        district=request.POST['district'],
        state=request.POST['state'],
        country=request.POST['country'],
        pin_number=request.POST['pin_number']
    )
    new_address.save()

    return JsonResponse({
        'success': True,
        'address': {
            'id': new_address.id,
            'name': new_address.name,
            'phone_number': new_address.phone_number,
            'house_name': new_address.house_name,
            'street_name': new_address.street_name,
            'district': new_address.district,
            'state': new_address.state,
            'country': new_address.country,
            'pin_number': new_address.pin_number,
        }
    })