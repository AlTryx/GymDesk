from typing import List, Optional
from core.domain.entities.resource import ResourceEntity
from core.domain.entities.timeslot import TimeSlotEntity
from core.application.interfaces.repositories import ResourceRepositoryInterface, TimeSlotRepositoryInterface
from datetime import datetime, timedelta


class ResourceService:

    def __init__(self, resource_repo: ResourceRepositoryInterface, timeslot_repo: TimeSlotRepositoryInterface):
        self.resource_repo = resource_repo
        self.timeslot_repo = timeslot_repo

    def create_resource(self, name: str, type: str, max_bookings: int, color_code: str) -> ResourceEntity:
        entity = ResourceEntity(
            id=None,
            name=name,
            type=type,
            max_bookings=max_bookings,
            color_code=color_code,
            created_at=None
        )
        return self.resource_repo.create(entity)

    def get_resource(self, resource_id: int) -> Optional[ResourceEntity]:
        return self.resource_repo.get_by_id(resource_id)

    def list_resources(self, type_filter: Optional[str] = None) -> List[ResourceEntity]:
        return self.resource_repo.list_all(type_filter)

    def update_resource(self, resource_id: int, name: str, type: str, max_bookings: int, color_code: str) -> ResourceEntity:
        entity = ResourceEntity(
            id=resource_id,
            name=name,
            type=type,
            max_bookings=max_bookings,
            color_code=color_code,
            created_at=None
        )
        return self.resource_repo.update(entity)

    def delete_resource(self, resource_id: int) -> bool:
        return self.resource_repo.delete(resource_id)

    def generate_timeslots(self, resource_id: int, start_date: datetime, end_date: datetime, duration_minutes: int = 60):
        resource = self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} не съществува")

        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            for hour in range(8, 22):
                slot_start = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
                slot_end = slot_start + timedelta(minutes=duration_minutes)

                entity = TimeSlotEntity(
                    id=None,
                    resource_id=resource_id,
                    start_time=slot_start,
                    end_time=slot_end,
                    is_available=True
                )

                self.timeslot_repo.create(entity)

            current_date += timedelta(days=1)