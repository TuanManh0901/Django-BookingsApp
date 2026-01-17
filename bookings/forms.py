from django import forms
from django.utils import timezone
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'num_adults', 'num_children']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date and booking_date < timezone.now().date():
            raise forms.ValidationError("Booking date cannot be in the past.")
        return booking_date
    
    def clean(self):
        cleaned_data = super().clean()
        num_adults = cleaned_data.get('num_adults', 0)
        num_children = cleaned_data.get('num_children', 0)
        total_people = num_adults + num_children
        
        if total_people == 0:
            raise forms.ValidationError("At least one person must be selected.")
        
        if self.tour:
            # Kiểm tra số chỗ còn trống
            available_seats = self.tour.get_available_seats()
            if total_people > available_seats:
                raise forms.ValidationError(
                    f"Không đủ chỗ! Tour chỉ còn {available_seats} chỗ trống, "
                    f"bạn đang đặt {total_people} chỗ."
                )
            
            total_price = total_people * self.tour.price
            cleaned_data['total_price'] = total_price
        
        return cleaned_data