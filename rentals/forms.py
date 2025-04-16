from django import forms
from .models import Booking, Location, Car
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['pickup_location', 'return_location', 'start_date', 'end_date']
        widgets = {
            'pickup_location': forms.Select(attrs={'class': 'form-select'} ),
            'return_location': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  # Changed from 'date' to 'datetime-local'
                    'class': 'form-control'
                }
            ),
            'end_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  # Changed from 'date' to 'datetime-local'
                    'class': 'form-control'
                }
            ),
        }
        labels = {
            'pickup_location': 'Место получения',
            'return_location': 'Место возврата',
            'start_date': 'Дата и время получения',
            'end_date': 'Дата и время возврата',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for locations
        try:
            default_location = Location.objects.first()
            if default_location:
                self.fields['pickup_location'].initial = default_location.id
                self.fields['return_location'].initial = default_location.id
        except:
            pass
        
        # Set minimum datetime (now) in the correct format for datetime-local
        from django.utils import timezone
        
        # Get current datetime and format it correctly for the input
        now = timezone.now()
        now = now.replace(microsecond=0)  # Remove microseconds
        min_datetime = now.strftime('%Y-%m-%dT%H:%M')  # Format: YYYY-MM-DDThh:mm
        
        self.fields['start_date'].widget.attrs['min'] = min_datetime
        self.fields['end_date'].widget.attrs['min'] = min_datetime
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Return date and time must be after pick-up date and time")
        
        # Validate minimum rental period (e.g., 1 hour)
        if start_date and end_date:
            min_rental_period = timedelta(hours=1)  # Use timedelta directly
            if end_date - start_date < min_rental_period:
                raise forms.ValidationError("Minimum rental period is 1 hour")
            
        return cleaned_data

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['name', 'brand', 'price_per_day', 'description', 'image', 
                  'year', 'mileage', 'fuel_type', 'transmission', 'seats', 
                  'category', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CarSearchForm(forms.Form):
    brand = forms.CharField(
        max_length=50,
        required=False,
        label="Марка"  # <-- Здесь задаётся label для form.brand.label
    )
    category = forms.ChoiceField(
        choices=[('', 'Все категории')] + list(Car._meta.get_field('category').choices),
        required=False,
        label="Категория"
    )
    transmission = forms.ChoiceField(
        choices=[('', 'Любая')] + list(Car._meta.get_field('transmission').choices),
        required=False,
        label="Коробка передач"
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Мин. цена (₽)"
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Макс. цена (₽)"
    )
    min_seats = forms.IntegerField(
        required=False,
        label="Мин. количество мест"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
