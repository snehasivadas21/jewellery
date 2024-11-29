from django.shortcuts import render,redirect,get_object_or_404
from .models import Category
from utils.decorators import admin_required
from django.contrib import messages
from django.db import IntegrityError

# Create your views here.
@admin_required
def list_category(request):
    categories = Category.objects.all().order_by('id')
    return render(request,'admin_side/list_category.html',{'categories':categories})

@admin_required
def create_category(request):
    if request.method =='POST':
        category_name = request.POST.get('category_name')
        stripped_category_name =category_name.strip()

        if not stripped_category_name:
            messages.error(request,'Category name cannot be empty.')
          
        if len(stripped_category_name) < 3:
            messages.error(request, 'Category name must be at least 3 characters long.')
            return redirect('create_category')
        try:
            category = Category.objects.create(category_name=category_name)
            messages.success(request, f'Category "{category_name}" created successfully.')
            return redirect('list_category')
        except IntegrityError:
            messages.error(request, f'Category "{category_name}" already exists.')
            return redirect('create_category')
        except Exception as e:
            messages.error(request, f'Failed to create category: {str(e)}')
            return redirect('create_category')

    return render(request, 'admin_side/create_category.html')


@admin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        slug = request.POST.get('slug')
        stripped_category_name = category_name.strip()
        stripped_slug = slug.strip()

        if not stripped_category_name:
            messages.error(request, 'Category name cannot be empty.')
            return redirect('edit-category', category_id=category_id)
        
        if len(stripped_category_name) < 3:
            messages.error(request, 'Category name must be at least 3 characters long.')
            return redirect('edit-category', category_id=category_id)

        if not stripped_slug:
            messages.error(request, 'Slug cannot be empty.')
            return redirect('edit-category', category_id=category_id)
        
        if len(stripped_slug) < 3:
            messages.error(request, 'Slug must be at least 3 characters long.')
            return redirect('edit-category', category_id=category_id)

        if Category.objects.filter(
            category_name__iexact=stripped_category_name
        ).exclude(id=category_id).exists():
            messages.error(request, f'Category "{category_name}" already exists.')
            return redirect('edit-category', category_id=category_id)

        if Category.objects.filter(
            slug__iexact=stripped_slug
        ).exclude(id=category_id).exists():
            messages.error(request, f'Slug "{slug}" is already in use by another category.')
            return redirect('edit-category', category_id=category_id)

        try:
            category.category_name = category_name
            category.slug = slug
            category.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category:list-category')
        except IntegrityError:
            messages.error(request, 'A database error occurred, please try again.')
            return redirect('edit-category', category_id=category_id)

    return render(request, 'admin_side/edit_category.html', {'category': category})

@admin_required
def category_is_available(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_available = not category.is_available
    category.save()
    return redirect('list_category')