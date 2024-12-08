from register.models import User
from social_core.pipeline.partial import partial
from social_django.models import UserSocialAuth
from django.contrib import messages
from django.shortcuts import redirect
from social_core.exceptions import AuthForbidden

@partial
def save_user_details(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    email = details.get('email')
    first_name = details.get('first_name')
    last_name = details.get('last_name')

    if not email or not first_name or not last_name:
        return strategy.redirect('/some-error-page/') 

    try:
        user = User.objects.get(email=email)
        if UserSocialAuth.objects.filter(user=user, provider='google-oauth2').exists():

            return {'is_new': False, 'user': user}
        else:

            UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid=details.get('uid'))
            return {'is_new': False, 'user': user}
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=details.get('phone_number', ''),
        )
        return {
            'is_new': True,
            'user': user
        }

def set_user_phone_number(backend, user, response, *args, **kwargs):
    phone_number = response.get('phone_number')
    if phone_number and not user.phone_number:
        user.phone_number = phone_number
        user.save()

def activate_user(user, *args, **kwargs):
    user.is_active = True
    user.save()
    
def check_if_user_blocked(user, *args, **kwargs):
    request = kwargs.get('request')

    if user.is_blocked:
        if request:
            # Log out the blocked user
            from django.contrib.auth import logout
            logout(request)

            # Notify the user
            messages.error(request, "Your account has been blocked. Please contact support.")
            return redirect('/blocked-user/')  # Redirect to a custom blocked user page

        # Raise exception if no request context
        raise AuthForbidden('Your account has been blocked.')

    return {
        'is_blocked': False,
        'user': user
    }







