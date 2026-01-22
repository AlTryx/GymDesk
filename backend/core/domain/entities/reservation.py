from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class ReservationEntity:

    id: Optional[int]
    user_id: int
    resource_id: int
    time_slot_id: int
    status: str = 'ACTIVE'  # ACTIVE or CANCELLED
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        # Валидация на ID-та
        if self.user_id <= 0:
            raise ValueError("user_id трябва да е положително число")

        if self.resource_id <= 0:
            raise ValueError("resource_id трябва да е положително число")

        if self.time_slot_id <= 0:
            raise ValueError("time_slot_id трябва да е положително число")

        # Валидация на status
        if self.status not in ['ACTIVE', 'CANCELLED']:
            raise ValueError(f"Status трябва да е ACTIVE или CANCELLED, а не '{self.status}'")

        # Валидация на notes
        if self.notes is not None and len(self.notes.strip()) == 0:
            self.notes = None

    def is_active(self) -> bool:
        return self.status == 'ACTIVE'

    def is_cancelled(self) -> bool:
        return self.status == 'CANCELLED'

    def cancel(self, current_time: Optional[datetime] = None) -> None:
        if self.is_cancelled():
            raise ValueError("Резервацията вече е отменена")

        if not self.is_active():
            raise ValueError("Само активни резервации могат да се отменят")

        self.status = 'CANCELLED'

    def can_be_cancelled(self) -> bool:
        return self.is_active()

    def has_notes(self) -> bool:
        return self.notes is not None and len(self.notes) > 0

    def update_notes(self, new_notes: str) -> None:
        if not new_notes or len(new_notes.strip()) == 0:
            self.notes = None
        else:
            self.notes = new_notes.strip()

    def __str__(self) -> str:
        return f"Reservation #{self.id} ({self.status})"