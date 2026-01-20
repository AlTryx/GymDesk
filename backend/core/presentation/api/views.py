from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
from core.application.services.reservation_service import ReservationService
from core.application.services.resource_service import ResourceService
from core.infrastructure.persistence.repositories.implementations import (
    UserRepository, ResourceRepository, TimeSlotRepository, ReservationRepository
)
from core.presentation.api.serializers import ReservationSerializer, ResourceSerializer, TimeSlotSerializer
from datetime import datetime


user_repo = UserRepository()
resource_repo = ResourceRepository()
timeslot_repo = TimeSlotRepository()
reservation_repo = ReservationRepository()

reservation_service = ReservationService(reservation_repo, user_repo, resource_repo, timeslot_repo)
resource_service = ResourceService(resource_repo, timeslot_repo)


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
        # owner is the authenticated user
        owner_id = request.user.id
        resources = resource_service.list_resources(type_filter, owner_id)

        return Response({'success': True, 'resources': [ResourceSerializer.to_dict(r) for r in resources]})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resource(request):
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body)
        owner_id = request.user.id

        resource = resource_service.create_resource(
            name=data['name'],
            type=data['type'],
            max_bookings=data['max_bookings'],
            color_code=data['color_code'],
            owner_id=owner_id
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

        # ensure resource belongs to user
        resource = resource_service.get_resource(resource_id)
        if not resource or resource.owner_id != request.user.id:
            return Response({'success': False, 'error': 'Resource не съществува или нямате достъп'}, status=status.HTTP_403_FORBIDDEN)

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
            # ensure resource belongs to user
            res = resource_repo.get_by_id(int(resource_id))
            if not res or res.owner_id != request.user.id:
                return Response({'success': False, 'error': 'Resource not found or access denied'}, status=status.HTTP_403_FORBIDDEN)
            timeslots = timeslot_repo.list_by_resource(int(resource_id))
        else:
            return Response({'success': False, 'error': 'Provide resource_id or date'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'timeslots': [TimeSlotSerializer.to_dict(t) for t in timeslots]})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)