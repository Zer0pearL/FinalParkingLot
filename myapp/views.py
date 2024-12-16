from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, LoginForm, BookingForm, VehicleForm, CustomUserChangeForm
from .models import  ParkingSpace, ParkingLot, Vehicle, Booking, User
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.forms import *
from django.contrib.auth import update_session_auth_hash
from django.db.models import F
from math import ceil
from django.db import transaction  
from decimal import Decimal
from django.utils import timezone




# Create your views here.

def home(request):
    # Get all vehicles for the user
    vehicles = Vehicle.objects.filter(user=request.user)

    vehicle_data = []
    for vehicle in vehicles:
        latest_booking = vehicle.latest_booking
        if latest_booking and latest_booking.end_time > timezone.now():
            remaining_time = latest_booking.end_time - timezone.now()
            hours = remaining_time.seconds // 3600
            minutes = (remaining_time.seconds % 3600) // 60
            vehicle_data.append({
                'vehicle': vehicle,
                'parking_lot': latest_booking.parking_space.parking_lot.name,
                'parking_space': latest_booking.parking_space.spot_number,
                'remaining_time': f"{hours} hours, {minutes} minutes",
                'latest_booking_id': latest_booking.id  # Make sure this is passed for the cancel button
            })
        else:
            vehicle_data.append({
                'vehicle': vehicle,
                'parking_lot': 'Not Parked',
                'parking_space': 'Not Parked',
                'remaining_time': "No active booking",
                'latest_booking_id': None  # No booking, no cancel button
            })

    return render(request, 'home.html', {'vehicle_data': vehicle_data})




def logout_view(request):
    logout(request)
    return redirect('login')


def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    booking.delete()
    messages.success(request, 'Successfuly Canceled')

    return redirect('home')

def book_parking(request, parking_lot_id):
    user = request.user
    parking_lot = get_object_or_404(ParkingLot, pk=parking_lot_id)
    available_spaces = ParkingSpace.objects.filter(parking_lot=parking_lot, is_occupied=False)
    available_vehicles = Vehicle.objects.filter(user=user, is_parked=False)

    if request.method == 'POST':
        form = BookingForm(request.POST, user=user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = user
            booking.parking_space = form.cleaned_data['parking_space']
            booking.vehicle = form.cleaned_data['vehicle']

            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            duration_seconds = (end_time - start_time).total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)

            total_hours = ceil(duration_seconds / 3600)  
            booking.cost = round(total_hours * 1.0, 2) 

            try:
                with transaction.atomic():
                    # Deduct the cost from the user's balance
                    user_profile = user.profile
                    if user_profile.balance >= booking.cost:  # Ensure the user has enough balance
                        user_profile.balance -= Decimal(booking.cost)
                        user_profile.save()

                        # Update the parking space and vehicle
                        booking.parking_space.is_occupied = True
                        booking.parking_space.save()
                        booking.vehicle.is_parked = True
                        booking.vehicle.save()

                        booking.save()

                        # Update the parking lot's revenue
                        ParkingLot.objects.filter(pk=parking_lot.id).update(revenue=F('revenue') + booking.cost)

                        messages.success(
                            request,
                            f"Your booking for vehicle {booking.vehicle.vehicle_number} at parking space {booking.parking_space.spot_number} has been confirmed.\n"
                            f"Duration: {hours} hours and {minutes} minutes.\n"
                            f"Cost: ${booking.cost:.2f} has been deducted from your balance."
                        )
                        return redirect('home')
                    else:
                        messages.error(request, "Insufficient balance for this booking.")
                        return redirect('book_parking', parking_lot_id=parking_lot_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('book_parking', parking_lot_id=parking_lot_id)
    else:
        form = BookingForm(initial={'parking_lot': parking_lot}, user=user)
        form.fields['parking_space'].queryset = available_spaces
        form.fields['vehicle'].queryset = available_vehicles
    return render(request, 'book_parking.html', {'form': form, 'available_spaces': available_spaces, 'parking_lot': parking_lot})


def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)  
            vehicle.user = request.user  
            vehicle.save()
            messages.success(request, 'Successfuly Added')

            return redirect('home')
    else:
        form = VehicleForm()
    return render(request, 'add_vehicle.html', {'form': form})


def select_parking_lot(request):
    parking_lots = ParkingLot.objects.all()
    return render(request, 'select_parking_lot.html', {'parking_lots': parking_lots})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import update_session_auth_hash

def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.instance)
            messages.success(request, 'Successfuly Edited Profile')
            return redirect('home')  
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('login')  
    return render(request, 'delete_profile.html', {'user': request.user})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Successfuly Changed Password')
            return redirect('home')  
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
def my_parking_lots(request):
    user = request.user  
    parking_lots = ParkingLot.objects.filter(user=user)  

    parking_lots_with_spaces = []
    for lot in parking_lots:
        spaces = lot.parkingspace_set.all()  
        parking_lots_with_spaces.append({
            'lot': lot,
            'spaces': spaces
        })

    bookings = Booking.objects.filter(user=user)

    return render(request, 'my_parking_lots.html', {
        'parking_lots_with_spaces': parking_lots_with_spaces,
        'bookings': bookings
    })