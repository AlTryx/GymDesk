from django.contrib import admin
from core.models import User, Resource, TimeSlot, Reservation

admin.site.register(User)
admin.site.register(Resource)
admin.site.register(TimeSlot)
admin.site.register(Reservation)