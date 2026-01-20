from django.urls import path
from core.presentation.api import views
from .auth_views import login, register
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/login/", login),
    path("auth/register/", register),
    path("auth/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path('reservations/create/', views.create_reservation, name='create_reservation'),
    # list reservations for authenticated user
    path('reservations/', views.list_user_reservations, name='list_user_reservations'),
    path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),

    path('resources/', views.list_resources, name='list_resources'),
    path('resources/create/', views.create_resource, name='create_resource'),

    path('timeslots/', views.list_timeslots, name='list_timeslots'),
    path('timeslots/generate/', views.generate_timeslots, name='generate_timeslots'),
]