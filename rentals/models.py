from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Car(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    # New fields for car details
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    mileage = models.IntegerField(null=True, blank=True)
    fuel_type = models.CharField(max_length=50, blank=True)
    transmission = models.CharField(max_length=50, blank=True, 
                                   choices=[('automatic', 'Автоматическая'), 
                                            ('manual', 'Механическая')])
    seats = models.IntegerField(default=5)
    category = models.CharField(max_length=50, blank=True,
                               choices=[('economy', 'Эконом'),
                                        ('compact', 'Компактный'),
                                        ('luxury', 'Люкс'),
                                        ('suv', 'Внедорожник'),
                                        ('van', 'Фургон')])

    def __str__(self):
        return f"{self.brand} {self.name}"

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.city}"

def get_default_location():
    # This will get the first location or create one if none exist
    location, created = Location.objects.get_or_create(
        name="Main Office",
        defaults={
            'address': '123 Main Street',
            'city': 'Cityville',
            'phone': '555-1234'
        }
    )
    return location.id

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='pickup_bookings',
        default=get_default_location
    )
    return_location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='return_bookings',
        default=get_default_location
    )
    start_date = models.DateTimeField()  # Changed from DateField
    end_date = models.DateTimeField()    # Changed from DateField
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_returned = models.BooleanField(default=False)
    actual_return_date = models.DateTimeField(null=True, blank=True)  # Changed from DateField

    def save(self, *args, **kwargs):
        if not self.total_price:
            # Calculate days as a float to account for partial days
            days = (self.end_date - self.start_date).total_seconds() / (24 * 3600)
            
            # Convert days from float to Decimal before multiplying
            from decimal import Decimal
            days_decimal = Decimal(str(days))  # Converting via string preserves precision
            self.total_price = days_decimal * self.car.price_per_day
            
            # Apply additional fee if different return location
            if self.pickup_location != self.return_location:
                self.total_price *= Decimal('1.1')  # Also use Decimal for multiplier
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.car.name} from {self.start_date} to {self.end_date}"
        
    @property
    def is_active(self):
        """Check if the booking is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date and not self.is_returned
        
    @property
    def is_overdue(self):
        """Check if the car is overdue for return"""
        today = date.today()
        return today > self.end_date and not self.is_returned