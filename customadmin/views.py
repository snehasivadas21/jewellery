from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from utils.decorators import admin_required
from register.models import User
from register.forms import UserRegistrationForm
from datetime import datetime
from order.models import OrderMain,OrderSub
from django.db.models import Sum,Count
from django.utils.timezone import now, timedelta
from django.utils import timezone


# Create your views here.
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Retrieve 'email' field
        password = request.POST.get('password')  # Retrieve 'password' field

        # Debugging: Print the values to verify
        print(f"Email: {email}, Password: {password}")

        user = authenticate(request, username=email, password=password)
        print(user)

        if user is not None:
            if user.is_staff:
                login(request,user)
                return redirect('admin_dashboard')
            else:
                messages.error(request,'you are not authorized to access this page.')
                return redirect('admin_login')
        else:
            # If authentication fails, display an error message
            messages.error(request, 'Invalid email or password.')
            return redirect('admin_login')  # Redirect back to the login page

    return render(request,'admin_side/admin_login.html')

@admin_required
def admin_dashboard(request):
    return render(request, 'admin_side/admin_dashboard.html',)

@admin_required
def user_list(request):
    users = User.objects.filter(is_admin=False)
    return render(request, 'admin_side/user-list.html', {'users': users})

@admin_required
def user_block(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = True
    user.save()
    messages.success(request, f'User {user.first_name} blocked successfully.')
    return redirect('user-list')


@admin_required
def user_unblock(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = False
    user.save()
    messages.success(request, f'User {user.first_name} unblocked successfully.')
    return redirect('user-list')

@admin_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def sales_report(request):
    filter_type=request.GET.get('filter',None)
    now=timezone.now()
    start_date=end_date=None

    if filter_type=='weekly':
        start_date=now-timedelta(days=now.weekday())
        end_date=now
    elif filter_type == 'monthly':
        start_date=now.replace(day=1)
        end_date=now
    if start_date and end_date:
        orders=OrderMain.objects.filter(
            order_status="Delivered",
            is_active=True,
            date__range=[start_date,end_date]
        ) 
    else:
        orders=OrderMain.objects.filter(
            order_status="Delivered",
            is_active=True
        )
    total_discount = orders.aggregate(total=Sum('discount_amount'))['total'] or 0
    total_orders=orders.aggregate(total=Count('id'))['total'] or 0
    total_order_amount=orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return render(request,'admin_side/salesreport.html',{
        'orders':orders,
        'total_discount':total_orders,
        'total_orders':total_orders,
        'total_order_amount':total_order_amount
    })          

def order_date_filter(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            try:
                start_date=datetime.strptime(start_date,'%Y-%m-%d').date()
                end_date=datetime.strptime(end_date,'%Y-%m-%d').date()
            except ValueError:
                return redirect('sales-report')

            orders = OrderMain.objects.filter(date__range=[start_date,end_date],order_status="Order Placed")
            total_discount =orders.aggregate(total=Sum('discount_amount'))['total'] or 0
            total_orders=orders.aggregate(total=Count('id'))['total'] or 0
            total_order_amount=orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            return render(request,'admin_side/salesreport.html',{
                'orders':orders,
                'total_discount':total_discount,
                'total_orders':total_orders,
                'total_orders_amount':total_order_amount,
            }) 
    return redirect('sales-report')   




