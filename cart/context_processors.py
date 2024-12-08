from .models import CartItem
from userprofile.models import Wishlist

def cart_and_wishlist_counts(request):
    cart_item_count = 0
    wishlist_item_count = 0
    
    if request.user.is_authenticated:
        cart_item_count = CartItem.objects.filter(cart__user=request.user, is_active=True).count()
        wishlist_item_count = Wishlist.objects.filter(user=request.user).count()

    return {
        'cart_item_count': cart_item_count,
        'wishlist_item_count': wishlist_item_count,
    }