import pytest
from datetime import datetime, timedelta
from core.domain.entities.user import UserEntity
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.domain.entities.reservation import ReservationEntity


class TestUserEntity:

    def test_create_user_entity(self):
        user = UserEntity(
            id=1,
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='USER',
            password_hash='hashed_password'
        )

        assert user.id == 1
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.role == 'USER'
        assert user.password_hash == 'hashed_password'

    def test_user_entity_str_representation(self):
        user = UserEntity(
            id=1,
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='USER',
            password_hash='hashed_password'
        )

        assert str(user) == 'test@example.com (USER)'


class TestResourceEntity:

    def test_create_valid_room_resource(self):
        resource = ResourceEntity(
            id=1,
            name='Conference Room A',
            type='ROOM',
            max_bookings=10,
            color_code='#FF5733',
            owner_id=1
        )

        assert resource.id == 1
        assert resource.name == 'Conference Room A'
        assert resource.type == 'ROOM'
        assert resource.max_bookings == 10
        assert resource.color_code == '#FF5733'
        assert resource.owner_id == 1
        assert resource.is_room() is True
        assert resource.is_equipment() is False

    def test_create_valid_equipment_resource(self):
        resource = ResourceEntity(
            id=2,
            name='Treadmill 1',
            type='EQUIPMENT',
            max_bookings=1,
            color_code='#33FF57'
        )

        assert resource.id == 2
        assert resource.name == 'Treadmill 1'
        assert resource.type == 'EQUIPMENT'
        assert resource.max_bookings == 1
        assert resource.color_code == '#33FF57'
        assert resource.owner_id is None
        assert resource.is_room() is False
        assert resource.is_equipment() is True

    def test_resource_validation_name_too_short(self):
        with pytest.raises(ValueError, match="Името на ресурса трябва да е поне 2 символа"):
            ResourceEntity(
                id=1,
                name='A',
                type='ROOM',
                max_bookings=5,
                color_code='#FF5733'
            )

    def test_resource_validation_invalid_type(self):
        with pytest.raises(ValueError, match="Type трябва да е ROOM или EQUIPMENT"):
            ResourceEntity(
                id=1,
                name='Test Resource',
                type='INVALID',
                max_bookings=5,
                color_code='#FF5733'
            )

    def test_resource_validation_max_bookings_too_low(self):
        with pytest.raises(ValueError, match="max_bookings трябва да е поне 1"):
            ResourceEntity(
                id=1,
                name='Test Resource',
                type='ROOM',
                max_bookings=0,
                color_code='#FF5733'
            )

    def test_resource_validation_max_bookings_too_high(self):
        with pytest.raises(ValueError, match="max_bookings не може да е повече от 100"):
            ResourceEntity(
                id=1,
                name='Test Resource',
                type='ROOM',
                max_bookings=101,
                color_code='#FF5733'
            )

    def test_resource_validation_invalid_color_code(self):
        with pytest.raises(ValueError, match="color_code трябва да е в hex формат"):
            ResourceEntity(
                id=1,
                name='Test Resource',
                type='ROOM',
                max_bookings=5,
                color_code='invalid'
            )

    def test_can_accept_reservations(self):
        resource = ResourceEntity(
            id=1,
            name='Test Resource',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )

        assert resource.can_accept_reservations(3) is True  # 3 < 5
        assert resource.can_accept_reservations(5) is False  # 5 == 5 (at capacity)
        assert resource.can_accept_reservations(6) is False  # 6 > 5

    def test_get_available_spots(self):
        resource = ResourceEntity(
            id=1,
            name='Test Resource',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )

        assert resource.get_available_spots(3) == 2  # 5 - 3 = 2
        assert resource.get_available_spots(5) == 0  # 5 - 5 = 0
        assert resource.get_available_spots(6) == 0  # max(0, 5 - 6) = 0

    def test_resource_entity_str_representation(self):
        resource = ResourceEntity(
            id=1,
            name='Test Resource',
            type='ROOM',
            max_bookings=5,
            color_code='#FF5733'
        )

        assert str(resource) == 'Test Resource (ROOM)'


class TestTimeSlotEntity:

    def test_create_timeslot_entity(self):
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)

        timeslot = TimeSlotEntity(
            id=1,
            resource_id=1,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )

        assert timeslot.id == 1
        assert timeslot.resource_id == 1
        assert timeslot.start_time == start_time
        assert timeslot.end_time == end_time
        assert timeslot.is_available is True
        assert timeslot.duration_minutes == 60

    def test_timeslot_is_in_past(self):
        # Use a fixed past time to avoid timezone issues
        past_time = datetime(2020, 1, 1, 10, 0, 0)
        future_time = datetime(2030, 1, 1, 10, 0, 0)

        past_timeslot = TimeSlotEntity(
            id=1,
            resource_id=1,
            start_time=past_time,
            end_time=past_time + timedelta(hours=1),
            is_available=True
        )

        future_timeslot = TimeSlotEntity(
            id=2,
            resource_id=1,
            start_time=future_time,
            end_time=future_time + timedelta(hours=1),
            is_available=True
        )

        assert past_timeslot.is_in_past() is True
        assert future_timeslot.is_in_past() is False

    def test_timeslot_entity_str_representation(self):
        start_time = datetime(2024, 1, 1, 10, 0)
        end_time = start_time + timedelta(hours=1)

        timeslot = TimeSlotEntity(
            id=1,
            resource_id=1,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )

        assert str(timeslot) == '2024-01-01 10:00 - 11:00 (60 min)'


class TestReservationEntity:

    def test_create_reservation_entity(self):
        reservation = ReservationEntity(
            id=1,
            user_id=1,
            resource_id=1,
            time_slot_id=1,
            status='ACTIVE',
            notes='Test reservation'
        )

        assert reservation.id == 1
        assert reservation.user_id == 1
        assert reservation.resource_id == 1
        assert reservation.time_slot_id == 1
        assert reservation.status == 'ACTIVE'
        assert reservation.notes == 'Test reservation'

    def test_reservation_entity_str_representation(self):
        reservation = ReservationEntity(
            id=1,
            user_id=1,
            resource_id=1,
            time_slot_id=1,
            status='ACTIVE'
        )

        assert str(reservation) == 'Reservation #1 (ACTIVE)'