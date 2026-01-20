from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from .profile_forms import UserProfileForm
from .forms import UserForm
from .models import UserProfile


@login_required
def user_profile(request):
    """Trang thông tin cá nhân của user"""
    # Auto-create profile if doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'profile': profile
    })


@login_required
def edit_profile(request):
    """Chỉnh sửa thông tin cá nhân"""
    # Auto-create profile if doesn't exist
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('user_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'user_form': user_form, 'form': profile_form})


def register(request):
    """Đăng ký tài khoản mới"""
    if request.user.is_authenticated:
        return redirect('tour_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify backend when multiple authentication backends are configured
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Chào mừng {user.username}! Tài khoản của bạn đã được tạo thành công.')
            return redirect('tour_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
