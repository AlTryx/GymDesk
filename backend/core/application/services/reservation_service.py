from typing import List, Optional
from datetime import datetime, timedelta
from core.domain.entities.reservation import ReservationEntity
from core.application.interfaces.repositories import (
    ReservationRepositoryInterface,
    UserRepositoryInterface,
    ResourceRepositoryInterface,
    TimeSlotRepositoryInterface
)


class ReservationService:

    def __init__(
            self,
            reservation_repo: ReservationRepositoryInterface,
            user_repo: UserRepositoryInterface,
            resource_repo: ResourceRepositoryInterface,
            timeslot_repo: TimeSlotRepositoryInterface
    ):
        self.reservation_repo = reservation_repo
        self.user_repo = user_repo
        self.resource_repo = resource_repo
        self.timeslot_repo = timeslot_repo

    def create_reservation(self, user_id: int, resource_id: int, timeslot_id: int, notes: Optional[str] = None) -> ReservationEntity:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} не съществува")

        resource = self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} не съществува")

        timeslot = self.timeslot_repo.get_by_id(timeslot_id)
        if not timeslot:
            raise ValueError(f"TimeSlot {timeslot_id} не съществува")

        if not timeslot.can_be_reserved():
            raise ValueError("TimeSlot не може да се резервира")

        current_count = self.reservation_repo.count_by_timeslot(timeslot_id, 'ACTIVE')

        if not resource.can_accept_reservations(current_count):
            raise ValueError("TimeSlot е пълен")

        entity = ReservationEntity(
            id=None,
            user_id=user_id,
            resource_id=resource_id,
            time_slot_id=timeslot_id,
            status='ACTIVE',
            notes=notes
        )

        return self.reservation_repo.create(entity)

    def get_user_reservations(self, user_id: int, status: Optional[str] = None) -> List[ReservationEntity]:
        return self.reservation_repo.list_by_user(user_id, status)

    def cancel_reservation(self, reservation_id: int, user_id: int) -> ReservationEntity:
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} не съществува")

        if reservation.user_id != user_id:
            user = self.user_repo.get_by_id(user_id)
            if not user or not user.is_admin():
                raise ValueError("Нямаш права да отменяш тази резервация")

        timeslot = self.timeslot_repo.get_by_id(reservation.time_slot_id)
        if timeslot and timeslot.start_time - datetime.now() < timedelta(hours=1):
            raise ValueError("Не може да отменяш по-малко от 1 час преди началото")

        reservation.cancel()
        return self.reservation_repo.update(reservation)

    def get_reservation(self, reservation_id: int) -> Optional[ReservationEntity]:
        return self.reservation_repo.get_by_id(reservation_id)