from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from core.domain.entities.user import UserEntity
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.domain.entities.reservation import ReservationEntity


class UserRepositoryInterface(ABC):

    @abstractmethod
    def create(self, entity: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def list_all(self) -> List[UserEntity]:
        pass

    @abstractmethod
    def update(self, entity: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class ResourceRepositoryInterface(ABC):

    @abstractmethod
    def create(self, entity: ResourceEntity) -> ResourceEntity:
        pass

    @abstractmethod
    def get_by_id(self, resource_id: int) -> Optional[ResourceEntity]:
        pass

    @abstractmethod
    def list_all(self, type_filter: Optional[str] = None) -> List[ResourceEntity]:
        pass

    @abstractmethod
    def update(self, entity: ResourceEntity) -> ResourceEntity:
        pass

    @abstractmethod
    def delete(self, resource_id: int) -> bool:
        pass


class TimeSlotRepositoryInterface(ABC):

    @abstractmethod
    def create(self, entity: TimeSlotEntity) -> TimeSlotEntity:
        pass

    @abstractmethod
    def get_by_id(self, slot_id: int) -> Optional[TimeSlotEntity]:
        pass

    @abstractmethod
    def list_by_resource(self, resource_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[TimeSlotEntity]:
        pass

    @abstractmethod
    def list_by_date(self, date: datetime) -> List[TimeSlotEntity]:
        pass

    @abstractmethod
    def update(self, entity: TimeSlotEntity) -> TimeSlotEntity:
        pass

    @abstractmethod
    def delete(self, slot_id: int) -> bool:
        pass


class ReservationRepositoryInterface(ABC):

    @abstractmethod
    def create(self, entity: ReservationEntity) -> ReservationEntity:
        pass

    @abstractmethod
    def get_by_id(self, reservation_id: int) -> Optional[ReservationEntity]:
        pass

    @abstractmethod
    def list_by_user(self, user_id: int, status: Optional[str] = None) -> List[ReservationEntity]:
        pass

    @abstractmethod
    def list_by_timeslot(self, timeslot_id: int, status: str = 'ACTIVE') -> List[ReservationEntity]:
        pass

    @abstractmethod
    def count_by_timeslot(self, timeslot_id: int, status: str = 'ACTIVE') -> int:
        pass

    @abstractmethod
    def update(self, entity: ReservationEntity) -> ReservationEntity:
        pass

    @abstractmethod
    def delete(self, reservation_id: int) -> bool:
        pass