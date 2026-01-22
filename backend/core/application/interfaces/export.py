"""
Export interfaces following SOLID principles.
Defines contracts for schedule export implementations (printing, calendar, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class ScheduleExportInterface(ABC):
    """Interface for exporting user schedules in different formats."""
    
    @abstractmethod
    def export(self, user_id: int, start_date: datetime, end_date: datetime) -> bytes:
        """
        Export user reservations for given date range.
        
        Args:
            user_id: User ID to export reservations for
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            Binary data in format-specific representation
            
        Raises:
            ValueError: If date range is invalid
            FileNotFoundError: If export cannot be generated
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """Return MIME type for this export format."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return file extension without dot (e.g., 'pdf', 'ics')."""
        pass
