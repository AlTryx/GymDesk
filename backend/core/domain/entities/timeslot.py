"""
Бизнес правила:
- TimeSlot принадлежи на един Resource (М:1)
- Един TimeSlot може да има няколко резервации (1:М)
- Може да се резервира само ако is_available = True
- Не може да се резервира минал TimeSlot
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Optional


@dataclass
class TimeSlotEntity:
    id: Optional[int]
    resource_id: int  # FK към Resource
    start_time: datetime
    end_time: datetime
    is_available: bool = True #open timeslot by default

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time трябва да е преди end_time")

        duration = (self.end_time - self.start_time).total_seconds() / 3600
        if duration > 24:
            raise ValueError("TimeSlot не може да е повече от 24 часа")
        
        if duration < 0.25:
            raise ValueError("TimeSlot трябва да е поне 15 минути")

        if self.resource_id <= 0:
            raise ValueError("resource_id трябва да е положително число")

    def is_in_past(self, current_time: Optional[datetime] = None) -> bool:
        if current_time is None:
            current_time = timezone.now()

        # If start_time is naive, make current_time naive for comparison
        if timezone.is_naive(self.start_time) and timezone.is_aware(current_time):
            current_time = timezone.make_naive(current_time)
        # If start_time is aware, make current_time aware for comparison
        elif timezone.is_aware(self.start_time) and timezone.is_naive(current_time):
            current_time = timezone.make_aware(current_time, timezone.get_current_timezone())

        return self.start_time < current_time

    def is_in_future(self, current_time: Optional[datetime] = None) -> bool:
        return not self.is_in_past(current_time)

    def can_be_reserved(self, current_time: Optional[datetime] = None) -> bool:
        return self.is_available and self.is_in_future(current_time)

    @property
    def duration_minutes(self):
        delta_time = self.end_time - self.start_time
        return int(delta_time.total_seconds() / 60)

    def duration_hours(self) -> float:
        return self.duration_minutes() / 60.0

    def overlaps_with(self, other_start: datetime, other_end: datetime) -> bool:
        return self.start_time < other_end and other_start < self.end_time

    def close_for_maintanance(self):
        if not self.is_available:
            raise ValueError("Слотът вече е затворен")
        self.is_available = False

    def open_for_reservations(self):
        if self.is_available:
            raise ValueError("Слотът вече е отворен")
        self.is_available = True

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')} ({self.duration_minutes} min)"