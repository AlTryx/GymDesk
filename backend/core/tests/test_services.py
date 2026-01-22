import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from core.application.services.reservation_service import ReservationService
from core.application.services.resource_service import ResourceService
from core.domain.entities.user import UserEntity
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.domain.entities.reservation import ReservationEntity


class TestReservationService:
    
    def setup_method(self):
        #Set up fixtures
        self.reservation_repo = Mock()
        self.user_repo = Mock()
        self.resource_repo = Mock()
        self.timeslot_repo = Mock()

        self.service = ReservationService(
            self.reservation_repo,
            self.user_repo,
            self.resource_repo,
            self.timeslot_repo
        )

    @pytest.mark.django_db
    def test_create_reservation_success(self):
        # Setup mocks
        user = UserEntity(id=1, email='user@example.com', first_name='Test', last_name='User',
                         role='USER', password_hash='hash')
        resource = ResourceEntity(id=1, name='Test Room', type='ROOM', max_bookings=5,
                                color_code='#FF5733')
        timeslot = TimeSlotEntity(id=1, resource_id=1,
                                start_time=datetime.now() + timedelta(hours=1),
                                end_time=datetime.now() + timedelta(hours=2),
                                is_available=True)

        self.user_repo.get_by_id.return_value = user
        self.resource_repo.get_by_id.return_value = resource
        self.timeslot_repo.get_by_id.return_value = timeslot
        self.reservation_repo.count_by_timeslot.return_value = 2  # Less than max_bookings

        # Mock the create method to return a reservation entity
        expected_reservation = ReservationEntity(
            id=1, user_id=1, resource_id=1, time_slot_id=1, status='ACTIVE', notes='Test notes'
        )
        self.reservation_repo.create = Mock(return_value=expected_reservation)

        # Execute
        result = self.service.create_reservation(1, 1, 1, 'Test notes')

        # Assert
        assert result == expected_reservation
        self.reservation_repo.create.assert_called_once()

    def test_create_reservation_user_not_found(self):
        self.user_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="User 1 не съществува"):
            self.service.create_reservation(1, 1, 1)

    def test_create_reservation_resource_not_found(self):
        user = UserEntity(id=1, email='user@example.com', first_name='Test', last_name='User',
                         role='USER', password_hash='hash')

        self.user_repo.get_by_id.return_value = user
        self.resource_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Resource 1 не съществува"):
            self.service.create_reservation(1, 1, 1)

    def test_create_reservation_timeslot_not_found(self):
        user = UserEntity(id=1, email='user@example.com', first_name='Test', last_name='User',
                         role='USER', password_hash='hash')
        resource = ResourceEntity(id=1, name='Test Room', type='ROOM', max_bookings=5,
                                color_code='#FF5733')

        self.user_repo.get_by_id.return_value = user
        self.resource_repo.get_by_id.return_value = resource
        self.timeslot_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="TimeSlot 1 не съществува"):
            self.service.create_reservation(1, 1, 1)

    def test_create_reservation_timeslot_unavailable(self):
        user = UserEntity(id=1, email='user@example.com', first_name='Test', last_name='User',
                         role='USER', password_hash='hash')
        resource = ResourceEntity(id=1, name='Test Room', type='ROOM', max_bookings=5,
                                color_code='#FF5733')
        timeslot = TimeSlotEntity(id=1, resource_id=1,
                                start_time=datetime.now() + timedelta(hours=1),
                                end_time=datetime.now() + timedelta(hours=2),
                                is_available=False)  # Not available

        self.user_repo.get_by_id.return_value = user
        self.resource_repo.get_by_id.return_value = resource
        self.timeslot_repo.get_by_id.return_value = timeslot

        with pytest.raises(ValueError, match="TimeSlot е затворен за резервации"):
            self.service.create_reservation(1, 1, 1)

    def test_create_reservation_timeslot_in_past(self):
        user = UserEntity(id=1, email='user@example.com', first_name='Test', last_name='User',
                         role='USER', password_hash='hash')
        resource = ResourceEntity(id=1, name='Test Room', type='ROOM', max_bookings=5,
                                color_code='#FF5733')
        timeslot = TimeSlotEntity(id=1, resource_id=1,
                                start_time=datetime.now() - timedelta(hours=2),  # Past
                                end_time=datetime.now() - timedelta(hours=1),    # Past
                                is_available=True)

        self.user_repo.get_by_id.return_value = user
        self.resource_repo.get_by_id.return_value = resource
        self.timeslot_repo.get_by_id.return_value = timeslot

        with pytest.raises(ValueError, match="TimeSlot е в миналото и не може да се резервира"):
            self.service.create_reservation(1, 1, 1)


class TestResourceService:

    def setup_method(self):
        #Set up fixtures
        self.resource_repo = Mock()
        self.timeslot_repo = Mock()

        self.service = ResourceService(self.resource_repo, self.timeslot_repo)

    def test_generate_timeslots_for_resource(self):
        # Setup
        resource = ResourceEntity(id=1, name='Test Room', type='ROOM', max_bookings=5,
                                color_code='#FF5733')

        self.resource_repo.get_by_id.return_value = resource

        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)  # 1 day later

        # Execute
        self.service.generate_timeslots(1, start_date, end_date, 60)

        # Assert - should create timeslots for each hour of each day
        # For 2 days with 60 min slots, should create 28 slots (14 hours per day * 2 days)
        assert self.timeslot_repo.create.call_count == 28

        # Verify the calls
        calls = self.timeslot_repo.create.call_args_list
        for i, call in enumerate(calls):
            args, kwargs = call
            timeslot_entity = args[0]
            assert timeslot_entity.resource_id == 1
            assert timeslot_entity.is_available is True
            # Check that times are sequential starting from 8 AM
            day = i // 14  # 14 slots per day
            hour = 8 + (i % 14)  # Start from 8 AM
            expected_start = start_date + timedelta(days=day, hours=hour)
            expected_end = expected_start + timedelta(minutes=60)
            # Make expected times timezone-aware like the service does
            from django.utils import timezone
            expected_start = timezone.make_aware(expected_start, timezone.get_current_timezone())
            expected_end = timezone.make_aware(expected_end, timezone.get_current_timezone())
            assert timeslot_entity.start_time == expected_start
            assert timeslot_entity.end_time == expected_end