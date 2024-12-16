from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("", views.register, name="register"),
    path("home", views.home, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path("book/", views.home),
    path("success", views.home),
    path('book-parking/<int:parking_lot_id>/', views.book_parking, name='book_parking'),
    path('select-parking-lot/', views.select_parking_lot, name='select_parking_lot'),
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('my-parking-lots/', views.my_parking_lots, name='my_parking_lots'),

]