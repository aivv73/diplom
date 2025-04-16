from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='rentals/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('book/<int:car_id>/', views.book_car, name='book_car'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('locations/', views.locations, name='locations'),
]

# Add this at the end of the file to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
