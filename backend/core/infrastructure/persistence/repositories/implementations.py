from typing import List, Optional
from datetime import datetime
from core.application.interfaces.repositories import (
    UserRepositoryInterface,
    ResourceRepositoryInterface,
    TimeSlotRepositoryInterface,
    ReservationRepositoryInterface
)
from core.domain.entities.user import UserEntity
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.domain.entities.reservation import ReservationEntity
from core.models import User, Resource, TimeSlot, Reservation


class UserRepository(UserRepositoryInterface):

    def create(self, entity: UserEntity) -> UserEntity:
        user = User.objects.create(
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role
        )
        user.set_password(entity.password_hash)
        user.save()
        return self._to_entity(user)

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        try:
            user = User.objects.get(id=user_id)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            user = User.objects.get(email=email)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None

    def list_all(self) -> List[UserEntity]:
        users = User.objects.all()
        return [self._to_entity(u) for u in users]

    def update(self, entity: UserEntity) -> UserEntity:
        user = User.objects.get(id=entity.id)
        user.email = entity.email
        user.first_name = entity.first_name
        user.last_name = entity.last_name
        user.role = entity.role
        user.save()
        return self._to_entity(user)

    def delete(self, user_id: int) -> bool:
        try:
            User.objects.filter(id=user_id).delete()
            return True
        except:
            return False

    def _to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            password_hash=model.password,
            role=model.role,
            created_at=model.date_joined
        )


class ResourceRepository(ResourceRepositoryInterface):

    def create(self, entity: ResourceEntity) -> ResourceEntity:
        resource = Resource.objects.create(
            name=entity.name,
            type=entity.type,
            max_bookings=entity.max_bookings,
            color_code=entity.color_code
        )
        return self._to_entity(resource)

    def get_by_id(self, resource_id: int) -> Optional[ResourceEntity]:
        try:
            resource = Resource.objects.get(id=resource_id)
            return self._to_entity(resource)
        except Resource.DoesNotExist:
            return None

    def list_all(self, type_filter: Optional[str] = None) -> List[ResourceEntity]:
        queryset = Resource.objects.all()
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        return [self._to_entity(r) for r in queryset]

    def update(self, entity: ResourceEntity) -> ResourceEntity:
        resource = Resource.objects.get(id=entity.id)
        resource.name = entity.name
        resource.type = entity.type
        resource.max_bookings = entity.max_bookings
        resource.color_code = entity.color_code
        resource.save()
        return self._to_entity(resource)

    def delete(self, resource_id: int) -> bool:
        try:
            Resource.objects.filter(id=resource_id).delete()
            return True
        except:
            return False

    def _to_entity(self, model: Resource) -> ResourceEntity:
        return ResourceEntity(
            id=model.id,
            name=model.name,
            type=model.type,
            max_bookings=model.max_bookings,
            color_code=model.color_code,
            created_at=model.created_at
        )


class TimeSlotRepository(TimeSlotRepositoryInterface):

    def create(self, entity: TimeSlotEntity) -> TimeSlotEntity:
        slot = TimeSlot.objects.create(
            resource_id=entity.resource_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
            is_available=entity.is_available
        )
        return self._to_entity(slot)

    def get_by_id(self, slot_id: int) -> Optional[TimeSlotEntity]:
        try:
            slot = TimeSlot.objects.get(id=slot_id)
            return self._to_entity(slot)
        except TimeSlot.DoesNotExist:
            return None

    def list_by_resource(self, resource_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimeSlotEntity]:
        queryset = TimeSlot.objects.filter(resource_id=resource_id)
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__lte=end_date)
        return [self._to_entity(s) for s in queryset]

    def list_by_date(self, date: datetime) -> List[TimeSlotEntity]:
        queryset = TimeSlot.objects.filter(start_time__date=date.date())
        return [self._to_entity(s) for s in queryset]

    def update(self, entity: TimeSlotEntity) -> TimeSlotEntity:
        slot = TimeSlot.objects.get(id=entity.id)
        slot.is_available = entity.is_available
        slot.save()
        return self._to_entity(slot)

    def delete(self, slot_id: int) -> bool:
        try:
            TimeSlot.objects.filter(id=slot_id).delete()
            return True
        except:
            return False

    def _to_entity(self, model: TimeSlot) -> TimeSlotEntity:
        return TimeSlotEntity(
            id=model.id,
            resource_id=model.resource_id,
            start_time=model.start_time,
            end_time=model.end_time,
            is_available=model.is_available
        )


class ReservationRepository(ReservationRepositoryInterface):

    def create(self, entity: ReservationEntity) -> ReservationEntity:
        reservation = Reservation.objects.create(
            user_id=entity.user_id,
            resource_id=entity.resource_id,
            time_slot_id=entity.time_slot_id,
            status=entity.status,
            notes=entity.notes
        )
        return self._to_entity(reservation)

    def get_by_id(self, reservation_id: int) -> Optional[ReservationEntity]:
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            return self._to_entity(reservation)
        except Reservation.DoesNotExist:
            return None

    def list_by_user(self, user_id: int, status: Optional[str] = None) -> List[ReservationEntity]:
        queryset = Reservation.objects.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)
        return [self._to_entity(r) for r in queryset.order_by('-created_at')]

    def list_by_timeslot(self, timeslot_id: int, status: str = 'ACTIVE') -> List[ReservationEntity]:
        queryset = Reservation.objects.filter(time_slot_id=timeslot_id, status=status)
        return [self._to_entity(r) for r in queryset]

    def count_by_timeslot(self, timeslot_id: int, status: str = 'ACTIVE') -> int:
        return Reservation.objects.filter(time_slot_id=timeslot_id, status=status).count()

    def update(self, entity: ReservationEntity) -> ReservationEntity:
        reservation = Reservation.objects.get(id=entity.id)
        reservation.status = entity.status
        reservation.notes = entity.notes
        reservation.save()
        return self._to_entity(reservation)

    def delete(self, reservation_id: int) -> bool:
        try:
            Reservation.objects.filter(id=reservation_id).delete()
            return True
        except:
            return False

    def _to_entity(self, model: Reservation) -> ReservationEntity:
        return ReservationEntity(
            id=model.id,
            user_id=model.user_id,
            resource_id=model.resource_id,
            time_slot_id=model.time_slot_id,
            status=model.status,
            notes=model.notes,
            created_at=model.created_at
        )