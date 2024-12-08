from django.shortcuts import render,redirect, get_object_or_404
from .models import Products,Category,Product_images,Product_Variant,Product_variant_images
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch,Avg,Count,Sum
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower,Coalesce
from utils.decorators import admin_required
from django.contrib import messages
from django.utils import timezone
from django.db import DataError
from decimal import Decimal,InvalidOperation
from userprofile.models import Wishlist
import re


@admin_required
def products_list(request):
    products = Products.objects.all().order_by('-created_at')
    return render(request, 'admin_side/products_list.html', {'products':products})

def product_detail(request,product_id):
    products=get_object_or_404(Products,id=product_id)
    images=Product_images.objects.filter(product=products)
    return render(request,'admin_side/product_details.html',{
        'products':products,
        'images':images
    })

@admin_required
def create_product(request):
    if request.method == 'POST':
        product_name=request.POST.get('product_name','').strip()
        product_description=request.POST.get('product_description','').strip()
        product_category_id=request.POST.get('product_category')
        price=request.POST.get('price','0').strip()
        offer_price=request.POST.get('offer_price','0').strip()
        is_active=request.POST.get('is_active')=='on'
        thumbnail=request.FILES.get('thumbnail')

        if not re.match(r"^[A-Za-z\s]+$",product_name):
            messages.error(request,'Product name must cantain only letters and spaces.')
            return redirect('create-product')
        
        try:
            price=Decimal(price)
            offer_price=Decimal(offer_price)
            if price<0 or offer_price<0:
                raise ValidationError('Price and offer price cannot be negative.')
            if offer_price>price:
                raise ValidationError('Offer price cannot be greater than the regular price.')
        except InvalidOperation:
            messages.error(request,'Price and offer price must be valid numbers.')
            return redirect('create-product')
        except ValidationError as e:
            messages.error(request,str(e)) 
            return redirect('create-product')
        if Products.objects.filter(product_name=product_name).exists():
            messages.error(request,f'Product with the name "{product_name}" already exists.')
            return redirect('create-product')
        
        category=get_object_or_404(Category,id=product_category_id)
        
        product=Products(
            product_name=product_name,
            product_description=product_description,
            product_category=category,
            price=price,
            offer_price=offer_price,
            thumbnail=thumbnail,
            is_active=is_active,
            created_at=timezone.now(),
            updated_at=timezone.now()

        )
        product.save()

        messages.success(request,f'Product "{product_name}" created succesfully.')
        return redirect('products-list')
    
    categories=Category.objects.all()
    return render(request,'admin_side/create_product.html',{'categories':categories})
        

@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    category_id = None  # Initialize the variable to avoid UnboundLocalError

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        category_id = request.POST.get('product_category')  # Fetch category_id from form submission
        price = request.POST.get('price').strip()
        offer_price = request.POST.get('offer_price').strip()
        is_active = request.POST.get('is_active') == 'on'
        thumbnail = request.FILES.get('thumbnail')

        # Stripped product details
        stripped_product_name = product_name.strip()
        stripped_product_description = product_description.strip()

        # Validation for product name
        if not re.match(r"^[A-Za-z ]+$", stripped_product_name):
            messages.error(request, 'Product name must contain only letters and spaces.')
            return redirect('edit_product', product_id=product_id)

        if len(stripped_product_name) < 3:
            messages.error(request, 'Product name must be at least 3 characters long.')
            return redirect('edit_product', product_id=product_id)

        # Price validation
        try:
            price = float(price)
            offer_price = float(offer_price)
            if price < 0 or offer_price < 0:
                raise ValidationError('Price and Offer Price cannot be negative.')
            if offer_price > price:
                raise ValidationError('Offer price cannot be greater than the regular price.')
        except ValueError:
            messages.error(request, 'Price and Offer Price must be valid numbers.')
            return redirect('edit_product', product_id=product_id)
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('edit_product', product_id=product_id)

        # Check for unique product name
        if Products.objects.filter(product_name__iexact=product_name).exclude(id=product_id).exists():
            messages.error(request, f'Product with the name "{stripped_product_name}" already exists.')
            return redirect('edit_product', product_id=product_id)

        # Update product details
        product.product_name = product_name
        product.product_description = product_description
        product.price = price
        product.offer_price = offer_price
        product.is_active = is_active

        # Update product category
        if category_id:
            try:
                product.product_category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                messages.error(request, 'Selected category does not exist.')
                return redirect('edit_product', product_id=product_id)

        # Update thumbnail if provided
        if thumbnail:
            product.thumbnail = thumbnail

        product.updated_at = timezone.now()
        product.save()

        messages.success(request, f'Product "{product_name}" updated successfully.')
        return redirect('product-detail', product_id=product_id)

    categories = Category.objects.all()
    return render(request, 'admin_side/edit_product.html', {
        'product': product,
        'categories': categories,
    })

@admin_required
def product_is_available(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.is_available = not product.is_available
    product.save()
    return redirect('products-list')

@admin_required
def product_status(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('product-detail',product_id=product.id)

@admin_required
def add_images(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        thumbnail = request.FILES.get('thumbnail')
        images = request.FILES.getlist('images')
        
        if thumbnail:
            product.thumbnail = thumbnail
            product.save()

        for image in images:
            Product_images.objects.create(product=product, images=image)

        return redirect('product-detail',product_id=product_id)

    return render(request, 'admin_side/add_images.html', {'product': product})


@admin_required
def add_variant(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    variants = Product_Variant.objects.filter(product=product)

    if request.method == 'POST':
        colour_name = request.POST.get('colour_name')
        variant_stock = request.POST.get('variant_stock')
        variant_status = request.POST.get('variant_status')
        weight = request.POST.get('weight')  # Value from frontend
        colour_code=request.POST.get('colour_code')

        # Validate color name
        stripped_colour_name = colour_name.strip()
        if not re.match("^[A-Za-z ]+$", stripped_colour_name):
            messages.error(request, 'Color name must contain only letters and spaces.')
            return redirect('add-variant', product_id=product_id)

        # Validate weight
        if weight not in ['Lightweight', 'Medium weight', 'Heavyweight']:
            messages.error(request, 'Invalid weight category.')
            return redirect('add-variant', product_id=product_id)

        # Validate stock
        try:
            variant_stock = int(variant_stock)
            if variant_stock < 0:
                raise ValidationError('Variant stock cannot be negative.')
        except ValueError:
            messages.error(request, 'Variant stock must be a valid number.')
            return redirect('add-variant', product_id=product_id)

        # Validate status
        if variant_status not in ['0', '1']:
            messages.error(request, 'Invalid variant status.')
            return redirect('add-variant', product_id=product_id)
        variant_status = bool(int(variant_status))

        # Check for duplicates
        variant_exists = Product_Variant.objects.filter(
            product=product,
            colour_name=stripped_colour_name,
            weight=weight
        ).exists()

        if variant_exists:
            messages.error(request, 'A variant with this color and weight already exists.')
            return redirect('add-variant', product_id=product_id)

        # Create variant
        variant = Product_Variant.objects.create(
            product=product,
            colour_name=colour_name,
            weight=weight,
            variant_stock=variant_stock,
            variant_status=variant_status,
            colour_code=colour_code
        )

        messages.success(request, 'Variant added successfully.')
        return redirect('add-variant-image', product_variant_id=variant.id)

    return render(request, 'admin_side/add_variant.html', {'product': product, 'variants': variants})

def add_variant_image(request, product_variant_id):
    product_variant = get_object_or_404(Product_Variant, id=product_variant_id)
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        
        if images:
            for image in images:
                Product_variant_images.objects.create(product_variant=product_variant, images=image)
            return redirect('variant-detail', product_id=product_variant.product.id)
        
        return HttpResponse("Invalid data", status=400)

    return render(request, 'admin_side/add_variant.image.html', {'product_variant': product_variant})


def delete_image(request, image_id):
    try:
        image = Product_variant_images.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'success': True})
    except Product_variant_images.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)


def variant_detail(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    variants = Product_Variant.objects.filter(product=product).prefetch_related('product_variant_images_set')
    context = {
        'product': product,
        'variants': variants,
    }
    return render(request, 'admin_side/variant_detail.html', context)

@admin_required
def variant_status(request, variant_id):
    variant = get_object_or_404(Product_Variant, id=variant_id)
    variant.variant_status = not variant.variant_status
    variant.save()
    return redirect('variant-detail', variant.product.id)


@admin_required
def edit_variant(request, variant_id):
    variant = get_object_or_404(Product_Variant, id=variant_id)
    variant_images = Product_variant_images.objects.filter(product_variant=variant)

    if request.method == 'POST':
        # gemstone = request.POST.get('variant_gemstone')
        colour_name = request.POST.get('colour_name')
        colour_code=request.POST.get('colour_code')
        weight = request.POST.get('weight')
        variant_stock = request.POST.get('variant_stock')
        variant_status = request.POST.get('variant_status') == 'on'

        stripped_colour_name = colour_name.strip() if colour_name else ''
        stripped_colour_code=colour_code.strip() if colour_code else ''
        stripped_weight = weight.strip() if weight else ''

        if not re.match("^[A-Za-z ]+$", stripped_colour_name):
            messages.error(request, 'Color name must contain only letters and spaces.')
            return redirect('edit-variant', variant_id=variant_id)


        if not stripped_weight:
            messages.error(request, 'weight  is required.')
            return redirect('edit-variant', variant_id=variant_id)
        
        if not stripped_colour_code:
            messages.error(request,'Color code is required.')
            return redirect('edit-varient',variant_id=variant_id)

        if Product_Variant.objects.filter(product=variant.product, colour_name=stripped_colour_name).exclude(id=variant_id).exists():
            messages.error(request, 'A variant with this color name already exists.')
            return redirect('edit-variant', variant_id=variant_id)

        # if Product_Variant.objects.filter(product=variant.product, weight=stripped_weight).exclude(id=variant_id).exists():
        #     messages.error(request, 'A variant with this weight already exists.')
        #     return redirect('edit-variant', variant_id=variant_id)

        try:
            variant_stock = int(variant_stock)
            if variant_stock < 0:
                raise ValidationError('Stock cannot be negative.')
        except ValueError:
            messages.error(request, 'Stock must be a valid integer.')
            return redirect('edit-variant', variant_id=variant_id)
        except ValidationError as e:
            messages.error(request, str(e))

        if not stripped_colour_name:
            messages.error(request, 'Color name is required.')
            return redirect('edit-variant', variant_id=variant_id)
        
        if not stripped_colour_code:
            messages.error(request,'Color code is required.')
            return redirect('edit-variant',variant_id=variant_id)

        if not stripped_weight:
            messages.error(request, 'weight code is required.')
            return redirect('edit-variant', variant_id=variant_id)

        # variant.gemstone = gemstone
        variant.colour_code=colour_code
        variant.colour_name = stripped_colour_name
        variant.weight = stripped_weight
        variant.variant_stock = variant_stock
        variant.variant_status = variant_status

        if request.FILES.get('images'):
            Product_variant_images.objects.create(
                product_variant=variant,
                images=request.FILES.get('images')
            )
        
        try:
            variant.save()
            messages.success(request, 'Variant updated successfully.')
        except DataError:
            messages.error(request, 'The value for one or more fields is out of range.')
            return redirect('edit-variant', variant_id=variant_id)

        return redirect('variant-detail', variant.product.id)

    return render(request, 'admin_side/edit_varient.html', {'variant': variant, 'variant_images': variant_images})





# user side product fuctions

def product_details_user(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    variants = Product_Variant.objects.filter(product=product).prefetch_related('product_variant_images_set')

    # Find related products by category

    # related_products = Products.objects.filter(
    #     product_category=product.product_category
    # ).exclude(id=product.id)[:3]

    related_products = Products.objects.exclude(id=product.id)[:3]
    
    has_purchased = False 
    if request.user.is_authenticated:
        has_purchased = product.user_has_purchased(request.user) 

    selected_variant = variants.first()
    variant_images = Product_variant_images.objects.none()
    if selected_variant:
        variant_images = selected_variant.product_variant_images_set.all()

    if selected_variant:
        variants = list(variants)
        variants.remove(selected_variant)
        variants.insert(0, selected_variant)

    for variant in variants:
        variant.image_urls = [image.images.url for image in variant.product_variant_images_set.all()[:5]]    

    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = Wishlist.objects.filter(user=request.user).values_list('variant_id', flat=True)

    # Ensure at least 3 images for sub-pictures
    # while len(variant_images) < 3:
    #     variant_images = list(variant_images) + [None]  # Add placeholders if not enough images

    context = {
        'product': product,
        'variants': variants,
        'selected_variant': selected_variant,
        'variant_images': variant_images,
        'user_wishlist':user_wishlist,
        'has_purchased':has_purchased,
        'related_products': related_products,
    }

    return render(request, 'user_side/product-details.html', context)


def shop_side(request):
    categories = Category.objects.filter(is_available=True)
    products = Products.objects.filter(is_active=True,product_category__is_available=True)
    search_query = request.GET.get('search_query', '')
    selected_categories = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    if selected_categories:
        products = products.filter(product_category__id__in=selected_categories)

    products = products.annotate(
        effective_price=Coalesce('offer_price', 'price')
    )    
    
    if min_price:
        products = products.filter(effective_price__gte=min_price)
    
    if max_price:
        products = products.filter(effective_price__lte=max_price)

    sort_by = request.GET.get('sort', 'featured')
    sort_options = {
        'price_low_high': 'effective_price',
        'price_high_low': '-effective_price',
        'popularity': '-review_count',
        'new_arrivals': '-created_at',
        'name_az': Lower('product_name'),
        'name_za': Lower('product_name').desc(),
        'inventory': '-total_stock'
    }

    if sort_by in sort_options:
        if sort_by == 'avg_rating':
          products = products.annotate(avg_rating=Avg('-reviews__rating')).order_by(sort_options[sort_by])
        elif sort_by == 'popularity':
            products = products.annotate(review_count=Count('reviews')).order_by(sort_options[sort_by])
        elif sort_by == 'inventory':
            products = products.annotate(total_stock=Sum('product_variant__variant_stock')).order_by(sort_options[sort_by])
        else:
            products = products.order_by(sort_options[sort_by])

    products = products.prefetch_related(
        Prefetch('product_variant_set',
                 queryset=Product_Variant.objects.filter(variant_status=True),
                 to_attr='active_variants'),
        'product_variant_set__product_variant_images_set'
    )

    paginator = Paginator(products, 6)
    page = request.GET.get('page')

    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    for product in products_paginated:
        if product.active_variants:
            variant = product.active_variants[0]
            image = variant.product_variant_images_set.first()
            product.image_url = image.images.url if image else product.thumbnail.url if product.thumbnail else None
        else:
            product.image_url = product.thumbnail.url if product.thumbnail else None

    context = {
        'categories': categories,
        'products': products_paginated,
        'current_sort': sort_by,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('user_side/product_list.html', {'products': products_paginated})
        return JsonResponse({'html': html})
    
    return render(request, 'user_side/shop_side.html', context)
