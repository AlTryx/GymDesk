from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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


@csrf_exempt
@require_http_methods(["POST"])
def create_reservation(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        resource_id = data.get('resource_id')
        timeslot_id = data.get('timeslot_id')
        notes = data.get('notes')

        reservation = reservation_service.create_reservation(user_id, resource_id, timeslot_id, notes)

        return JsonResponse({
            'success': True,
            'reservation': ReservationSerializer.to_dict(reservation)
        }, status=201)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_user_reservations(request, user_id):
    try:
        status = request.GET.get('status')
        reservations = reservation_service.get_user_reservations(user_id, status)

        return JsonResponse({
            'success': True,
            'reservations': [ReservationSerializer.to_dict(r) for r in reservations]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cancel_reservation(request, reservation_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')

        reservation = reservation_service.cancel_reservation(reservation_id, user_id)

        return JsonResponse({
            'success': True,
            'reservation': ReservationSerializer.to_dict(reservation)
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_resources(request):
    try:
        type_filter = request.GET.get('type')
        resources = resource_service.list_resources(type_filter)

        return JsonResponse({
            'success': True,
            'resources': [ResourceSerializer.to_dict(r) for r in resources]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_resource(request):
    try:
        data = json.loads(request.body)

        resource = resource_service.create_resource(
            name=data['name'],
            type=data['type'],
            max_bookings=data['max_bookings'],
            color_code=data['color_code']
        )

        return JsonResponse({
            'success': True,
            'resource': ResourceSerializer.to_dict(resource)
        }, status=201)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_timeslots(request):
    try:
        data = json.loads(request.body)
        resource_id = data['resource_id']
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date'])
        duration = data.get('duration_minutes', 60)

        resource_service.generate_timeslots(resource_id, start_date, end_date, duration)

        return JsonResponse({'success': True, 'message': 'TimeSlots generated'})
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_timeslots(request):
    try:
        resource_id = request.GET.get('resource_id')
        date_str = request.GET.get('date')

        if date_str:
            date = datetime.fromisoformat(date_str)
            timeslots = timeslot_repo.list_by_date(date)
        elif resource_id:
            timeslots = timeslot_repo.list_by_resource(int(resource_id))
        else:
            return JsonResponse({'success': False, 'error': 'Provide resource_id or date'}, status=400)

        return JsonResponse({
            'success': True,
            'timeslots': [TimeSlotSerializer.to_dict(t) for t in timeslots]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)