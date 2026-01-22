import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
from core.models import Resource, TimeSlot, Reservation
from datetime import datetime, timedelta

User = get_user_model()


class TestAuthentication(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_success(self):
        url = '/api/auth/login/'
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('role', response.data)

    def test_login_invalid_credentials(self):
        url = '/api/auth/login/'
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    def test_register_success(self):
        url = '/api/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user_id', response.data)

        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')

class TestReservationAPI(APITestCase):

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.resource = Resource.objects.create(
            name='Test Room',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )
        start_time = datetime.now() + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        self.timeslot = TimeSlot.objects.create(
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )

        # Authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_create_reservation_success(self):
        url = '/api/reservations/create/'
        data = {
            'resource_id': self.resource.id,
            'timeslot_id': self.timeslot.id,
            'notes': 'Test reservation'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('reservation', response.data)

    def test_create_reservation_conflict(self):
        # Create a resource with max_bookings=1
        conflict_resource = Resource.objects.create(
            name='Conflict Room',
            type='ROOM',
            max_bookings=1,
            color_code='#FF5733'
        )
        
        # First, create a reservation
        Reservation.objects.create(
            user=self.user,
            resource=conflict_resource,
            time_slot=self.timeslot,
            status='ACTIVE'
        )

        url = '/api/reservations/create/'
        data = {
            'resource_id': conflict_resource.id,
            'timeslot_id': self.timeslot.id,
            'notes': 'Conflicting reservation'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_cancel_reservation_success(self):
        # Create a reservation first
        reservation = Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot,
            status='ACTIVE'
        )

        url = f'/api/reservations/{reservation.id}/cancel/'
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('reservation', response.data)
        self.assertEqual(response.data['reservation']['status'], 'CANCELLED')

        # Verify reservation was cancelled in database
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'CANCELLED')

    def test_export_weekly_schedule_html(self):
        # Create a reservation for the user
        Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot,
            status='ACTIVE'
        )

        url = '/api/export/weekly-schedule-print/'
        start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        data = {
            'start_date': start_date,
            'end_date': end_date
        }

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        self.assertIn('sedmichnia_grafik', response['Content-Disposition'])

    def test_export_calendar_ics(self):
        # Create a reservation for the user
        Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot,
            status='ACTIVE'
        )

        url = '/api/export/calendar.ics'
        start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        data = {
            'start_date': start_date,
            'end_date': end_date
        }

        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/calendar; charset=utf-8')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
        self.assertIn('.ics', response['Content-Disposition'])
        # Check that response contains iCalendar content
        content = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', content)
        self.assertIn('END:VCALENDAR', content)

    def test_create_reservation_unauthenticated(self):
        # Remove authentication
        self.client.force_authenticate(user=None)

        url = '/api/reservations/create/'
        data = {
            'resource_id': self.resource.id,
            'timeslot_id': self.timeslot.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation_invalid_resource(self):
        url = '/api/reservations/create/'
        data = {
            'resource_id': 999,  # Non-existent resource
            'timeslot_id': self.timeslot.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_get_user_reservations(self):
        # Create a reservation first
        Reservation.objects.create(
            user=self.user,
            resource=self.resource,
            time_slot=self.timeslot,
            status='ACTIVE'
        )

        url = '/api/reservations/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['reservations']), 1)

        reservation_data = response.data['reservations'][0]
        self.assertEqual(reservation_data['resource_id'], self.resource.id)
        self.assertEqual(reservation_data['status'], 'ACTIVE')


class TestResourceAPI(APITestCase):

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        # Authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_get_resources(self):
        # Create some resources
        Resource.objects.create(
            name='Room A',
            type='ROOM',
            max_bookings=10,
            color_code='#FF5733'
        )
        Resource.objects.create(
            name='Treadmill 1',
            type='EQUIPMENT',
            max_bookings=1,
            color_code='#33FF57'
        )

        url = '/api/resources/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['resources']), 2)

    def test_create_resource_as_admin(self):
        self.client.force_authenticate(user=self.admin)

        url = '/api/resources/create/'
        data = {
            'name': 'New Conference Room',
            'type': 'ROOM',
            'max_bookings': 20,
            'color_code': '#FF5733'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

        # Check resource was created
        resource = Resource.objects.get(name='New Conference Room')
        self.assertEqual(resource.type, 'ROOM')
        self.assertEqual(resource.max_bookings, 20)

    def test_create_resource_as_regular_user(self):
        self.client.force_authenticate(user=self.user)

        url = '/api/resources/create/'
        data = {
            'name': 'New Room',
            'type': 'ROOM',
            'max_bookings': 5,
            'color_code': '#FF5733'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTimeSlotAPI(APITestCase):

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.resource = Resource.objects.create(
            name='Test Room',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )
        # Authenticate the client
        self.client.force_authenticate(user=self.user)

    def test_get_timeslots_for_resource(self):
        # Create some timeslots
        start_time = datetime.now() + timedelta(hours=1)
        for i in range(3):
            TimeSlot.objects.create(
                resource=self.resource,
                start_time=start_time + timedelta(hours=i),
                end_time=start_time + timedelta(hours=i+1),
                is_available=True
            )

        url = f'/api/timeslots/?resource_id={self.resource.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['timeslots']), 3)

    @patch('core.presentation.api.views.resource_service.generate_timeslots')
    def test_generate_timeslots_as_admin(self, mock_generate):
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        self.client.force_authenticate(user=admin)

        mock_generate.return_value = None

        url = '/api/timeslots/generate/'
        data = {
            'resource_id': self.resource.id,
            'start_date': '2024-01-01',
            'end_date': '2024-01-02',
            'duration_minutes': 60
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_generate.assert_called_once()