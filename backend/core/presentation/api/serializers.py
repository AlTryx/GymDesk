from core.domain.entities.user import UserEntity
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.domain.entities.reservation import ReservationEntity


class UserSerializer:
    @staticmethod
    def to_dict(entity: UserEntity) -> dict:
        return {
            'id': entity.id,
            'email': entity.email,
            'first_name': entity.first_name,
            'last_name': entity.last_name,
            'full_name': entity.full_name,
            'role': entity.role,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        }


class ResourceSerializer:
    @staticmethod
    def to_dict(entity: ResourceEntity) -> dict:
        return {
            'id': entity.id,
            'name': entity.name,
            'type': entity.type,
            'max_bookings': entity.max_bookings,
            'color_code': entity.color_code,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        }


class TimeSlotSerializer:
    @staticmethod
    def to_dict(entity: TimeSlotEntity) -> dict:
        return {
            'id': entity.id,
            'resource_id': entity.resource_id,
            'start_time': entity.start_time.isoformat(),
            'end_time': entity.end_time.isoformat(),
            'is_available': entity.is_available,
            'duration_minutes': entity.duration_minutes()
        }


class ReservationSerializer:
    @staticmethod
    def to_dict(entity: ReservationEntity) -> dict:
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'resource_id': entity.resource_id,
            'time_slot_id': entity.time_slot_id,
            'status': entity.status,
            'notes': entity.notes,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        }