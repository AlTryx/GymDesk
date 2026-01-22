"""
Export interfaces following SOLID principles.
Defines contracts for schedule export implementations (printing, calendar, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class ScheduleExportInterface(ABC):
    
    @abstractmethod
    def export(self, user_id: int, start_date: datetime, end_date: datetime) -> bytes:
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass
