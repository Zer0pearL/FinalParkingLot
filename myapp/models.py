from django.db import models
from django.contrib.auth.models import User
from math import ceil
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ParkingLot(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    

class ParkingSpace(models.Model):
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE)
    spot_number = models.IntegerField()
    is_occupied = models.BooleanField(default=False)


class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=20)  
    is_parked = models.BooleanField(default=False)
    @property
    def latest_booking(self):
        return self.booking_set.order_by('-start_time').first()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    parking_space = models.ForeignKey(ParkingSpace, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    def delete(self, *args, **kwargs):
        self.parking_space.is_occupied = False
        self.parking_space.save()
        self.vehicle.is_parked = False
        self.vehicle.save()
        super().delete(*args, **kwargs)
    def save(self, *args, **kwargs):
        duration_seconds = (self.end_time - self.start_time).total_seconds()
        total_hours = ceil(duration_seconds / 3600)  

        self.cost = round(total_hours * 1.00, 2)  
        
        super().save(*args, **kwargs)