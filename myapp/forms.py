from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import Vehicle, Booking, ParkingSpace, User
from django.forms.widgets import DateTimeInput
from django.utils import timezone
from datetime import timedelta

class LoginForm(AuthenticationForm):
    pass

class RegistrationForm(UserCreationForm):
    pass

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle', 'parking_space', 'start_time', 'end_time']
        widgets = {
            'start_time': DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        current_time = timezone.now()

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("Start time must be before end time.")
            if start_time < current_time:
                raise forms.ValidationError("Start time cannot be in the past.")
            if (end_time - start_time) < timedelta(hours=1):
                raise forms.ValidationError("End time must be at least one hour after start time.")
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(user=user, is_parked=False)
        self.fields['vehicle'].label_from_instance = lambda obj: obj.vehicle_number
        self.fields['parking_space'].label_from_instance = lambda obj: f"Parking Space: {obj.spot_number}"
    


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'vehicle_type']
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')