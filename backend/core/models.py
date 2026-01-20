from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=[('USER', 'User'), ('ADMIN', 'Admin')],
        default='USER'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
    
    def save(self, *args, **kwargs):
        # Ensure superusers are marked as ADMIN role so front-end role checks work
        if self.is_superuser and self.role != 'ADMIN':
            self.role = 'ADMIN'
        super().save(*args, **kwargs)


class Resource(models.Model):
    # Owner of the resource; nullable to allow existing resources to remain global
    # and to ease migration. In the future you may want to make this non-nullable.
    owner = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='resources')
    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=20,
        choices=[('ROOM', 'Room'), ('EQUIPMENT', 'Equipment')]
    )
    max_bookings = models.IntegerField(default=1)
    color_code = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resources'


class TimeSlot(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'time_slots'
        unique_together = ['resource', 'start_time', 'end_time']


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='reservations')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Active'), ('CANCELLED', 'Cancelled')],
        default='ACTIVE'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reservations'