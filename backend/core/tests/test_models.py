import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models import User, Resource, TimeSlot, Reservation
from datetime import datetime, timedelta


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'USER')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        self.assertEqual(superuser.role, 'ADMIN')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_user_str_representation(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), 'test@example.com')


class ResourceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='testpass123'
        )

    def test_create_room_resource(self):
        resource = Resource.objects.create(
            name='Conference Room A',
            type='ROOM',
            max_bookings=10,
            color_code='#FF5733',
            owner=self.user
        )
        self.assertEqual(resource.name, 'Conference Room A')
        self.assertEqual(resource.type, 'ROOM')
        self.assertEqual(resource.max_bookings, 10)
        self.assertEqual(resource.color_code, '#FF5733')
        self.assertEqual(resource.owner, self.user)

    def test_create_equipment_resource(self):
        resource = Resource.objects.create(
            name='Treadmill 1',
            type='EQUIPMENT',
            max_bookings=1,
            color_code='#33FF57'
        )
        self.assertEqual(resource.name, 'Treadmill 1')
        self.assertEqual(resource.type, 'EQUIPMENT')
        self.assertEqual(resource.max_bookings, 1)
        self.assertEqual(resource.color_code, '#33FF57')
        self.assertIsNone(resource.owner)

    def test_resource_str_representation(self):
        resource = Resource.objects.create(
            name='Test Resource',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )
        self.assertEqual(str(resource), 'Test Resource')


class TimeSlotModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='owner@example.com',
            username='timeslot_owner',
            password='testpass123'
        )
        self.resource = Resource.objects.create(
            name='Test Room',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733',
            owner=self.user
        )

    def test_create_timeslot(self):
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        timeslot = TimeSlot.objects.create(
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )

        self.assertEqual(timeslot.resource, self.resource)
        self.assertEqual(timeslot.start_time, start_time)
        self.assertEqual(timeslot.end_time, end_time)
        self.assertTrue(timeslot.is_available)

    def test_timeslot_str_representation(self):
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        timeslot = TimeSlot.objects.create(
            resource=self.resource,
            start_time=start_time,
            end_time=end_time
        )

        expected_str = f"{self.resource.name}: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"
        self.assertEqual(str(timeslot), expected_str)


class ReservationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )
        self.resource = Resource.objects.create(
            name='Test Room',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        self.timeslot = TimeSlot.objects.create(
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )

    def test_create_reservation(self):
        reservation = Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot,
            status='ACTIVE',
            notes='Test reservation'
        )

        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.resource, self.resource)
        self.assertEqual(reservation.time_slot, self.timeslot)
        self.assertEqual(reservation.status, 'ACTIVE')
        self.assertEqual(reservation.notes, 'Test reservation')

    def test_reservation_str_representation(self):
        reservation = Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot
        )

        expected_str = f"{self.user.email} - {self.resource.name} ({self.timeslot.start_time.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(reservation), expected_str)