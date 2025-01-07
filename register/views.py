from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_protect
from .forms import EmailAuthenticationForm
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import login,logout
from .models import User
from django.utils import timezone
from dateutil.parser import parse
from django.conf import settings
from .forms import UserRegistrationForm
from .signals import user_registered
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail,BadHeaderError
from django.contrib.auth.forms import SetPasswordForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.encoding import force_bytes
from django.http import JsonResponse
from category.models import Category
from product.models import Products


def index(request):
    return render(request, 'index.html')

def home_page(request):
    categories=Category.objects.all()
    products =Products.objects.filter(is_active=True)
    return render(request,'user_side/index.html',{'categories':categories,'products':products})

def register(request):
    if request.method == 'POST':
        form =UserRegistrationForm(request.POST)
        if form.is_valid():
            user_data = form.save(commit=False)
            user_data.is_active = False

            request.session['user_data']={
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
                'email': user_data.email,
                'phone_number': user_data.phone_number,
                'password': form.cleaned_data.get('password') 
            }

            user_registered.send(sender=register,user=user_data,request=request)

            messages.success(request, 'OTP has been sent to your email. Please verify to complete registration.')
            return redirect('verify_otp')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_side/signup.html', {'form': form})

@csrf_protect
def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        otp_generation_time_str = request.session.get('otp_generation_time')

        if otp_generation_time_str:
            try:
                otp_generation_time = parse(otp_generation_time_str)
                current_time = timezone.now()
                otp_valid_duration = timedelta(minutes=2)

                if current_time - otp_generation_time <= otp_valid_duration:
                    if otp == request.session.get('otp'):
                        user_data = request.session.get('user_data')
                        if user_data:
                            user = User.objects.create(
                                first_name=user_data.get('first_name'),
                                last_name=user_data.get('last_name'),
                                email=user_data.get('email'),
                                phone_number=user_data.get('phone_number')
                            )
                            user.set_password(user_data.get('password'))  
                            user.is_active = True
                            user.save()

                            
                            request.session.flush()

                            messages.success(request, 'Your account has been activated successfully.')
                            return redirect('login') 
                        else:
                            messages.error(request, 'User data not found. Please register again.')
                    else:
                        messages.error(request, 'Invalid OTP. Please try again.')
                else:
                    messages.error(request, 'OTP has expired. Please resent OTP.')
            except ValueError:
                messages.error(request, 'Invalid OTP generation time format.')
        else:
            messages.error(request, 'OTP generation time not found. Please register again.')

    return render(request, 'user_side/otp.html')

def resend_otp(request):
    user_data = request.session.get('user_data')
    if user_data:
        otp = get_random_string(length=6, allowed_chars='1234567890')
        print(otp)
        otp_generation_time = timezone.now().isoformat()
        
        request.session['otp'] = otp
        request.session['otp_generation_time'] = otp_generation_time

        send_mail(
            'Resend OTP Code',
            f'Your new OTP code is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user_data['email']],
            fail_silently=False,
        )
        messages.success(request, 'A new OTP has been sent to your email.')
    else:
        messages.error(request, 'User data not found. Please register again.')
    return redirect('verify_otp')


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active and not user.is_blocked:  
                login(request, user)
                # messages.success(request, f"Welcome, {user.email}! You have successfully logged in.")
                return redirect('home_page')
            else:
                messages.error(request, "This account is inactive. Please contact support.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'user_side/login.html', {'form': form})

def logout_view(request):
    logout(request)
    # messages.success(request, "You have successfully logged out.")
    return redirect('index')

def about_us(request):
    return render(request,'user_side/about.html')

def contact(request):
    return render(request,'user_side/contact.html')
 

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "user_side/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': 'eternagem.site',
                        'site_name': 'ETERNAGEM',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
                    }
                    email_content = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email_content,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password-reset-done")
    
    password_reset_form = PasswordResetForm()
    return render(request, "user_side/password_reset.html", {"password_reset_form": password_reset_form})


def password_reset_done(request):
    return render(request, 'user_side/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been set. You may go ahead and log in now.')
                return redirect('password-reset-complete')
            else:
                print(form.errors)
        else:
            form = SetPasswordForm(user)
        return render(request, 'user_side/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link was invalid, possibly because it has already been used. Please request a new password reset.')
        return redirect('password-reset')


def password_reset_complete(request):
    return render(request, 'user_side/password_reset_complete.html')
  
