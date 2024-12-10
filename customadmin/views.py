from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from utils.decorators import admin_required
from register.models import User
from register.forms import UserRegistrationForm


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




