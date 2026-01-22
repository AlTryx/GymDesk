from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
from core.application.services.reservation_service import ReservationService
from core.application.services.resource_service import ResourceService
from core.application.services.export_service import WeeklySchedulePrintService, ICalendarExportService
from core.infrastructure.persistence.repositories.implementations import (
    UserRepository, ResourceRepository, TimeSlotRepository, ReservationRepository
)
from core.presentation.api.serializers import ReservationSerializer, ResourceSerializer, TimeSlotSerializer
from datetime import datetime
from django.http import HttpResponse


user_repo = UserRepository()
resource_repo = ResourceRepository()
timeslot_repo = TimeSlotRepository()
reservation_repo = ReservationRepository()

reservation_service = ReservationService(reservation_repo, user_repo, resource_repo, timeslot_repo)
resource_service = ResourceService(resource_repo, timeslot_repo)

# Export services
weekly_schedule_service = WeeklySchedulePrintService(reservation_repo, resource_repo, timeslot_repo, user_repo)
icalendar_service = ICalendarExportService(reservation_repo, user_repo)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_reservation(request):
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        resource_id = data.get('resource_id')
        timeslot_id = data.get('timeslot_id')
        notes = data.get('notes')

        # Use authenticated user
        user_id = request.user.id

        reservation = reservation_service.create_reservation(user_id, resource_id, timeslot_id, notes)

        return Response({'success': True, 'reservation': ReservationSerializer.to_dict(reservation)}, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_reservations(request):
    try:
        status_filter = request.GET.get('status')
        # If admin, list ALL reservations; otherwise only the authenticated user's
        if getattr(request.user, 'role', None) == 'ADMIN':
            reservations = reservation_repo.list_all(status_filter)
        else:
            user_id = request.user.id
            reservations = reservation_service.get_user_reservations(user_id, status_filter)

        return Response({'success': True, 'reservations': [ReservationSerializer.to_dict(r) for r in reservations]})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_reservation(request, reservation_id):
    try:
        # authenticated user
        user_id = request.user.id

        reservation = reservation_service.cancel_reservation(reservation_id, user_id)

        return Response({'success': True, 'reservation': ReservationSerializer.to_dict(reservation)})
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resources(request):
    try:
        type_filter = request.GET.get('type')
        # Resources are gym-owned and visible to all users. Only admins can create them.
        resources = resource_service.list_resources(type_filter, None)

        return Response({'success': True, 'resources': [ResourceSerializer.to_dict(r) for r in resources]})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resource(request):
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        # Only admins may create resources (resources are gym-owned)
        if not getattr(request.user, 'role', None) == 'ADMIN':
            return Response({'success': False, 'error': 'Неавторизирано: само администратор може да добавя ресурси'}, status=status.HTTP_403_FORBIDDEN)

        # Create as global gym resource (owner stays null)
        resource = resource_service.create_resource(
            name=data['name'],
            type=data['type'],
            max_bookings=data['max_bookings'],
            color_code=data['color_code'],
            owner_id=None
        )

        return Response({'success': True, 'resource': ResourceSerializer.to_dict(resource)}, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_timeslots(request):
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        resource_id = data['resource_id']
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        duration = data.get('duration_minutes', 60)

        # Only admins may generate timeslots for resources
        if not getattr(request.user, 'role', None) == 'ADMIN':
            return Response({'success': False, 'error': 'Неавторизирано: само администратор може да генерира слотове'}, status=status.HTTP_403_FORBIDDEN)

        # ensure resource exists
        resource = resource_service.get_resource(resource_id)
        if not resource:
            return Response({'success': False, 'error': 'Resource не съществува'}, status=status.HTTP_404_NOT_FOUND)

        resource_service.generate_timeslots(resource_id, start_date, end_date, duration)

        return Response({'success': True, 'message': 'TimeSlots generated'})
    except ValueError as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_timeslots(request):
    try:
        resource_id = request.GET.get('resource_id')
        date_str = request.GET.get('date')

        if date_str:
            date = datetime.fromisoformat(date_str)
            timeslots = timeslot_repo.list_by_date(date)
        elif resource_id:
            # Resources are visible to all users; just ensure the resource exists
            res = resource_repo.get_by_id(int(resource_id))
            if not res:
                return Response({'success': False, 'error': 'Resource not found'}, status=status.HTTP_404_NOT_FOUND)
            timeslots = timeslot_repo.list_by_resource(int(resource_id))
        else:
            return Response({'success': False, 'error': 'Provide resource_id or date'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'timeslots': [TimeSlotSerializer.to_dict(t) for t in timeslots]})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ======================== Export Endpoints ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_weekly_schedule_print(request):
    """
    Export user's weekly schedule as HTML/printable format.
    Query params: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
    """
    try:
        user_id = request.user.id
        
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'success': False, 'error': 'start_date и end_date са задължителни (YYYY-MM-DD формат)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'success': False, 'error': 'Невалиден формат на дата. Използвайте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        html_content = weekly_schedule_service.export(user_id, start_date, end_date)
        
        response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'inline; filename="sedmichnia_grafik_{start_date_str}_do_{end_date_str}.html"'
        
        return response
        
    except ValueError as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': f'Грешка при експорт: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_calendar_ics(request):
    """
    Export user's reservations as iCalendar (.ics) file.
    Query params: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
    """
    try:
        user_id = request.user.id
        
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'success': False, 'error': 'start_date и end_date са задължителни (YYYY-MM-DD формат)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'success': False, 'error': 'Невалиден формат на дата. Използвайте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ics_content = icalendar_service.export(user_id, start_date, end_date)
        
        response = HttpResponse(ics_content, content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="gymdesk_calendar_{start_date_str}_do_{end_date_str}.ics"'
        
        return response
        
    except ValueError as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': f'Грешка при експорт: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )