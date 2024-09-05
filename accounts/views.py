from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from .models import CustomUser
from recipes.models import Recipe
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import pyotp
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')
    else:
        return render(request, 'accounts/login.html', {})

def logout_user(request):
    logout(request)
    return redirect('index')

def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
    return totp.now()

def signup_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['signup_data'] = request.POST
            email = form.cleaned_data['email']

            send_mail(
                'Your OTP Verification Code',
                f'Your OTP is {otp}. It is valid for 5 minutes.',
                'your_email@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        session_otp = request.session.get('otp')

        if user_otp == session_otp:
            signup_data = request.session.get('signup_data')
            form = CustomUserCreationForm(signup_data)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'accounts/otp.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('edit_profile')
    
    else:
        profile_form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/editprofile.html', {
        'profile_form': profile_form,
    })

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect('forgot_password')

        otp = generate_otp()  # Use the same OTP generation method
        request.session['otp'] = otp
        request.session['reset_user_id'] = user.id

        # Send OTP to the user's email
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is {otp}. It is valid for 5 minutes.',
            'your_email@gmail.com',
            [email],
            fail_silently=False,
        )

        return redirect('verify_reset_otp')

    return render(request, 'accounts/forgotpassword.html')

def verify_reset_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        session_otp = request.session.get('otp')

        if user_otp == session_otp:
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_reset_otp')

    return render(request, 'accounts/otp.html')

def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get('password')
        reset_user_id = request.session.get('reset_user_id')

        if reset_user_id:
            user = CustomUser.objects.get(id=reset_user_id)
            user.password = make_password(new_password)
            user.save()

            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')

    return render(request, 'accounts/resetpassword.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Your password has been successfully changed!')
            return redirect('change_password')
    
    else:
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/changepassword.html', {
        'password_form': password_form,
    })

@login_required
def profile(request):
    user = request.user
    return render(request, 'accounts/myprofile.html', {'user': user})

def user_profile(request, username):
    if request.user.is_authenticated and request.user.username == username:
        return redirect('myprofile')
    
    user = get_object_or_404(CustomUser, username=username)
    context = {
        'user': user,
    }
    return render(request, 'accounts/userprofile.html', context)

def follow_user(request, username):
    target_user = get_object_or_404(CustomUser, username=username)
    if request.user.is_authenticated:
        if target_user not in request.user.following_list.all():
            request.user.following_list.add(target_user)
            request.user.following_count += 1
            target_user.follower_count += 1
            target_user.follower_list.add(request.user)
        else:
            request.user.following_list.remove(target_user)
            request.user.following_count -= 1
            target_user.follower_count -= 1
            target_user.follower_list.remove(request.user)

        request.user.save()
        target_user.save()

    return redirect('user_profile', username=username)

def user_uploaded_recipes(request, username):
    user = get_object_or_404(CustomUser, username=username)
    recipes = Recipe.objects.filter(uploader=user)
    
    context = {
        'user': user,
        'recipes': recipes,
    }
    return render(request, 'accounts/userrecipes.html', context)

def user_followers(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followers = user.follower_list.all()

    context = {
        'user': user,
        'followers': followers,
    }
    return render(request, 'accounts/followers.html', context)

def user_followings(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followings = user.following_list.all()
    
    context = {
        'user': user,
        'followings': followings,
    }
    return render(request, 'accounts/followings.html', context)