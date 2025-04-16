from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import activate
from datetime import date
from .models import Car, Booking, Location
from .forms import BookingForm, CarSearchForm


def home(request):
    # Get 3 random cars to feature on the home page
    featured_cars = Car.objects.filter(is_available=True).order_by('?')[:3]
    return render(request, 'rentals/home.html', {'featured_cars': featured_cars})

def register(request):
    activate('ru')  # Set the language to Russian
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'rentals/register.html', {'form': form})

def car_list(request):
    form = CarSearchForm(request.GET or None)
    cars = Car.objects.all()
    
    if form.is_valid():
        brand = form.cleaned_data.get('brand')
        if brand:
            cars = cars.filter(brand__icontains=brand)
            
        category = form.cleaned_data.get('category')
        if category:
            cars = cars.filter(category=category)
            
        transmission = form.cleaned_data.get('transmission')
        if transmission:
            cars = cars.filter(transmission=transmission)
            
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            cars = cars.filter(price_per_day__gte=min_price)
            
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            cars = cars.filter(price_per_day__lte=max_price)
            
        min_seats = form.cleaned_data.get('min_seats')
        if min_seats:
            cars = cars.filter(seats__gte=min_seats)
    
    return render(request, 'rentals/car_list.html', {'cars': cars, 'form': form})

@login_required
def book_car(request, car_id):
    car = Car.objects.get(id=car_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            
            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                car=car,
                start_date__lt=booking.end_date,
                end_date__gt=booking.start_date
            )
            
            if overlapping_bookings.exists():
                return render(request, 'rentals/booking.html', {'form': form, 'car': car, 'error': 'Car is already booked for these dates and times!'})
            
            booking.save()
            return redirect('dashboard')
    else:
        form = BookingForm()
    return render(request, 'rentals/booking.html', {'form': form, 'car': car})

@login_required
def dashboard(request):
    today = date.today()
    bookings = Booking.objects.filter(user=request.user).order_by('-start_date')
    
    # Active bookings (not returned)
    active_bookings = bookings.filter(is_returned=False)
    
    # Bookings that need to be returned today
    return_today = active_bookings.filter(end_date=today)
    
    # Overdue bookings
    overdue_bookings = active_bookings.filter(end_date__lt=today)
    
    # Past bookings (returned or expired)
    past_bookings = bookings.filter(end_date__lt=today, is_returned=True)
    
    # Upcoming bookings
    upcoming_bookings = bookings.filter(start_date__gt=today)
    
    return render(request, 'rentals/dashboard.html', {
        'active_bookings': active_bookings,
        'return_today': return_today,
        'overdue_bookings': overdue_bookings,
        'past_bookings': past_bookings,
        'upcoming_bookings': upcoming_bookings,
    })

# Add this view function

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'rentals/car_detail.html', {'car': car})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if the booking can be cancelled (start date is in the future)
    from django.utils import timezone
    now = timezone.now()
    
    if booking.start_date > now:
        # Optional: Add cancellation fee logic here if needed
        # For example: if (booking.start_date - now).days < 2: add fee
        
        # Delete the booking
        booking.delete()
        
        # Add a success message
        from django.contrib import messages
        messages.success(request, "Booking cancelled successfully!")
    else:
        from django.contrib import messages
        messages.error(request, "Cannot cancel a booking that has already started or completed.")
    
    return redirect('dashboard')

def locations(request):
    locations = Location.objects.all()
    return render(request, 'rentals/locations.html', {'locations': locations})