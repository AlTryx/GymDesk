from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(["POST"])
def register(request):
    data = request.data
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if User.objects.filter(email=email).exists():
        return Response({"success": False, "error": "Email already used"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user_id": user.id,
    })

@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({"success": False, "error": "Invalid credentials"}, status=400)

    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user_id": user.id
    })
