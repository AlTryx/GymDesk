from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ResourceEntity:
    id: Optional[int]
    name: str
    type: str
    max_bookings: int
    color_code: str
    created_at: Optional[datetime] = None
    owner_id: Optional[int] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        #Name validation
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Името на ресурса трябва да е поне 2 символа")

        #Type validation
        if self.type not in ['ROOM', 'EQUIPMENT']:
            raise ValueError(f"Type трябва да е ROOM или EQUIPMENT, не '{self.type}'")

        #Max Bookings Validation
        if self.max_bookings < 1:
            raise ValueError("max_bookings трябва да е поне 1")
        if self.max_bookings > 100:
            raise ValueError("max_bookings не може да е повече от 100")

        #Color code validation
        if not self.color_code.startswith('#') or len(self.color_code) != 7:
            raise ValueError("color_code трябва да е в hex формат (#RRGGBB)")

    def is_room(self) -> bool:
        return self.type == 'ROOM'

    def is_equipment(self) -> bool:
        return self.type == 'EQUIPMENT'

    def can_accept_reservations(self, current_reservations_count: int) -> bool:
        return current_reservations_count < self.max_bookings

    def get_available_spots(self, current_reservations_count: int) -> int:
        return max(0, self.max_bookings - current_reservations_count)

