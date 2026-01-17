from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'cccd', 'date_of_birth', 'gender', 'address']
        labels = {
            'phone': 'Số điện thoại',
            'cccd': 'CCCD/CMND',
            'date_of_birth': 'Ngày sinh',
            'gender': 'Giới tính',
            'address': 'Địa chỉ',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại'
            }),
            'cccd': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập CCCD/CMND'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }, choices=[('', '-- Chọn giới tính --'), ('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác')]),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập địa chỉ của bạn',
                'rows': 3
            }),
        }

