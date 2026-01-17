from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email của bạn'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tên (không bắt buộc)'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ (không bắt buộc)'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại'
        })
    )
    cccd = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CCCD/CMND'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Ngày sinh'
        })
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[('', '-- Chọn giới tính --'), ('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác')],
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Địa chỉ',
            'rows': 3
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'cccd', 
                  'date_of_birth', 'gender', 'address', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thêm Bootstrap class
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tên đăng nhập'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })
        
        # Dịch username help_text sang tiếng Việt
        self.fields['username'].help_text = mark_safe(
            '<small class="form-text text-muted">'
            'Bắt buộc. Tối đa 150 ký tự. Chỉ sử dụng chữ cái, số và @/./+/-/_ .'
            '</small>'
        )
        
        # Dịch các thông báo lỗi password validation
        self.fields['password1'].help_text = mark_safe(
            '<small class="form-text text-muted">'
            '• Mật khẩu không được quá giống với thông tin cá nhân của bạn.<br>'
            '• Mật khẩu phải có ít nhất 8 ký tự.<br>'
            '• Mật khẩu không được là mật khẩu thường được sử dụng.<br>'
            '• Mật khẩu không được chỉ toàn số.'
            '</small>'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Lưu thông tin profile
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.cccd = self.cleaned_data.get('cccd', '')
            user.profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            user.profile.gender = self.cleaned_data.get('gender', '')
            user.profile.address = self.cleaned_data.get('address', '')
            user.profile.save()
        return user
