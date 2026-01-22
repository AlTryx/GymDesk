"""
Export service implementations using SOLID principles.
Handles PDF printing and iCalendar exports.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import io
from abc import ABC, abstractmethod

# Import the interface
from core.application.interfaces.export import ScheduleExportInterface
from core.infrastructure.persistence.repositories.implementations import (
    ReservationRepository,
    UserRepository,
    ResourceRepository,
    TimeSlotRepository
)


class WeeklySchedulePrintService(ScheduleExportInterface):
    """
    Generates HTML/PDF printable weekly schedule.
    Implements single responsibility principle - handles only PDF generation.
    """
    
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        resource_repo: ResourceRepository,
        timeslot_repo: TimeSlotRepository,
        user_repo: UserRepository
    ):
        self.reservation_repo = reservation_repo
        self.resource_repo = resource_repo
        self.timeslot_repo = timeslot_repo
        self.user_repo = user_repo
    
    def export(self, user_id: int, start_date: datetime, end_date: datetime) -> bytes:
        """
        Generate HTML for weekly schedule that can be printed to PDF.
        Returns HTML as bytes.
        """
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Fetch reservations for the date range
        reservations = self.reservation_repo.list_by_user_and_date_range(
            user_id, start_date, end_date, status='ACTIVE'
        )
        
        html = self._generate_html(user, reservations, start_date, end_date)
        return html.encode('utf-8')
    
    def _generate_html(self, user: Any, reservations: List[Any], start_date: datetime, end_date: datetime) -> str:
        """Generate HTML for printable weekly schedule."""
        
        # Group reservations by date
        by_date = self._group_by_date(reservations)
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Седмичен график - {user.email}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; padding: 20px; background: white; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 15px; }}
        .header h1 {{ color: #333; font-size: 24px; margin-bottom: 5px; }}
        .header p {{ color: #666; font-size: 14px; }}
        .date-range {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; }}
        .schedule-grid {{ display: grid; gap: 20px; }}
        .day-section {{ border: 1px solid #ddd; border-radius: 8px; overflow: hidden; page-break-inside: avoid; }}
        .day-header {{ background: #f0f0f0; padding: 12px 15px; font-weight: bold; font-size: 16px; border-bottom: 1px solid #ddd; }}
        .reservations {{ padding: 0; }}
        .reservation {{ padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: start; }}
        .reservation:last-child {{ border-bottom: none; }}
        .reservation-info {{ flex: 1; }}
        .resource-name {{ font-weight: bold; color: #333; margin-bottom: 5px; }}
        .time {{ color: #666; font-size: 14px; margin-bottom: 3px; }}
        .resource-type {{ display: inline-block; background: #e0e0e0; padding: 2px 8px; border-radius: 3px; font-size: 12px; color: #555; }}
        .notes {{ color: #888; font-size: 12px; margin-top: 5px; font-style: italic; }}
        .empty-day {{ padding: 15px; color: #999; text-align: center; }}
        .color-box {{ width: 12px; height: 12px; border-radius: 3px; margin-right: 10px; flex-shrink: 0; margin-top: 2px; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 15px; }}
        @media print {{
            body {{ padding: 0; }}
            .day-section {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Мой Седмичен График</h1>
        <p>GymDesk Резервационна Система</p>
    </div>
    <div class="date-range">
        {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')} | Потребител: {user.email}
    </div>
    <div class="schedule-grid">
"""
        
        # Generate day sections
        current = start_date.date()
        end = end_date.date()
        
        while current <= end:
            day_reservations = by_date.get(current.isoformat(), [])
            day_name = self._get_day_name(current)
            
            html += f"""
        <div class="day-section">
            <div class="day-header">{day_name} - {current.strftime('%d.%m.%Y')}</div>
            <div class="reservations">
"""
            
            if not day_reservations:
                html += '<div class="empty-day">Няма резервации</div>'
            else:
                for res in day_reservations:
                    html += self._format_reservation_html(res)
            
            html += """
            </div>
        </div>
"""
            current += timedelta(days=1)
        
        html += f"""
    </div>
    <div class="footer">
        Генерирано на: {datetime.now().strftime('%d.%m.%Y %H:%M')}
    </div>
</body>
</html>
"""
        return html
    
    def _group_by_date(self, reservations: List[Any]) -> Dict[str, List[Any]]:
        """Group reservations by date."""
        result = {}
        for res in reservations:
            # Assuming timeslot has start_time
            date_key = res.time_slot.start_time.date().isoformat()
            if date_key not in result:
                result[date_key] = []
            result[date_key].append(res)
        
        # Sort each day's reservations by time
        for key in result:
            result[key].sort(key=lambda r: r.time_slot.start_time)
        
        return result
    
    def _format_reservation_html(self, reservation: Any) -> str:
        """Format a single reservation as HTML."""
        resource = reservation.resource
        timeslot = reservation.time_slot
        
        color_box = f'<div class="color-box" style="background-color: {resource.color_code};"></div>'
        
        html = f"""
                <div class="reservation">
                    {color_box}
                    <div class="reservation-info">
                        <div class="resource-name">{resource.name}</div>
                        <div class="time">
                            {timeslot.start_time.strftime('%H:%M')} - {timeslot.end_time.strftime('%H:%M')}
                        </div>
                        <span class="resource-type">{resource.type}</span>
"""
        
        if reservation.notes:
            html += f'                        <div class="notes">Бележка: {reservation.notes}</div>\n'
        
        html += """
                    </div>
                </div>
"""
        return html
    
    def _get_day_name(self, date: Any) -> str:
        """Get Bulgarian day name."""
        days = ['Понеделник', 'Вторник', 'Сряда', 'Четвъртък', 'Петък', 'Събота', 'Неделя']
        return days[date.weekday()]
    
    def get_content_type(self) -> str:
        return 'text/html'
    
    def get_file_extension(self) -> str:
        return 'html'


class ICalendarExportService(ScheduleExportInterface):
    """
    Generates iCalendar (.ics) file for importing reservations into calendar apps.
    Implements single responsibility principle - handles only .ics generation.
    """
    
    def __init__(
        self,
        reservation_repo: ReservationRepository,
        user_repo: UserRepository
    ):
        self.reservation_repo = reservation_repo
        self.user_repo = user_repo
    
    def export(self, user_id: int, start_date: datetime, end_date: datetime) -> bytes:
        """
        Generate iCalendar file (.ics format).
        """
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Fetch reservations for the date range
        reservations = self.reservation_repo.list_by_user_and_date_range(
            user_id, start_date, end_date, status='ACTIVE'
        )
        
        ics_content = self._generate_ics(user, reservations)
        return ics_content.encode('utf-8')
    
    def _generate_ics(self, user: Any, reservations: List[Any]) -> str:
        """Generate iCalendar file content."""
        now = datetime.now().isoformat().replace(':', '').replace('-', '') + 'Z'
        
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//GymDesk//Reservations//BG
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:GymDesk - Мои Резервации
X-WR-TIMEZONE:Europe/Sofia
BEGIN:VTIMEZONE
TZID:Europe/Sofia
BEGIN:STANDARD
DTSTART:19700101T000000
TZOFFSETFROM:+0300
TZOFFSETTO:+0200
TZNAME:EET
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:19700101T030000
TZOFFSETFROM:+0200
TZOFFSETTO:+0300
TZNAME:EEST
END:DAYLIGHT
END:VTIMEZONE
"""
        
        # Add events
        for res in reservations:
            event = self._format_ics_event(res, now)
            ics += event
        
        ics += "END:VCALENDAR\n"
        return ics
    
    def _format_ics_event(self, reservation: Any, now: str) -> str:
        """Format a single reservation as iCalendar event."""
        resource = reservation.resource
        timeslot = reservation.time_slot
        
        # Format dates for iCalendar (YYYYMMDDTHHMMSS format)
        dtstart = timeslot.start_time.isoformat().replace(':', '').replace('-', '')
        dtend = timeslot.end_time.isoformat().replace(':', '').replace('-', '')
        
        # Create unique UID
        uid = f"gymdesk-res-{reservation.id}@gymdesk.local"
        
        # Clean text for iCalendar (escape special chars)
        description = self._escape_ics_text(f"{resource.type}: {resource.name}")
        if reservation.notes:
            description += f"\\nБележка: {self._escape_ics_text(reservation.notes)}"
        
        event = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now}
DTSTART;TZID=Europe/Sofia:{dtstart}
DTEND;TZID=Europe/Sofia:{dtend}
SUMMARY:{self._escape_ics_text(resource.name)}
DESCRIPTION:{description}
LOCATION:GymDesk
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
"""
        return event
    
    def _escape_ics_text(self, text: str) -> str:
        """Escape special characters for iCalendar format."""
        # Replace newlines with \n, escape commas, semicolons, and backslashes
        text = text.replace('\\', '\\\\')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '')
        text = text.replace(';', '\\;')
        text = text.replace(',', '\\,')
        return text
    
    def get_content_type(self) -> str:
        return 'text/calendar'
    
    def get_file_extension(self) -> str:
        return 'ics'
