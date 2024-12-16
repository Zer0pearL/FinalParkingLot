from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Booking)
admin.site.register(ParkingLot)
admin.site.register(ParkingSpace)
admin.site.register(Vehicle)
admin.site.register(UserProfile)
