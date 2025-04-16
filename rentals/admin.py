from django.contrib import admin
from .models import Car, Location, Booking
from django.utils import timezone

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'price_per_day', 'is_available')
    list_filter = ('brand', 'is_available')
    search_fields = ('brand', 'name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address')
    list_filter = ('city',)
    search_fields = ('name', 'city', 'address')

def mark_as_returned(modeladmin, request, queryset):
    queryset.update(is_returned=True, actual_return_date=timezone.now().date())
mark_as_returned.short_description = "Mark selected bookings as returned"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'start_date', 'end_date', 'is_returned', 'is_overdue')
    list_filter = ('is_returned', 'start_date', 'end_date')
    search_fields = ('user__username', 'car__name', 'car__brand')
    actions = [mark_as_returned]
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"