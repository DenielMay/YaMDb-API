from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import Admin
from .serializers import (
    RegistrationSerializer, ConfirmationCodeSerializer,
    UserSerializer, UserEditSerializer,
)
from reviews.models import User


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """Пользователь отправляет POST-запрос с параметрами email и username на
    эндпоинт /api/v1/auth/signup/. Сервис YaMDB отправляет письмо с кодом
    подтверждения (confirmation_code) на указанный адрес email.
    """

    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"])
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="Код авторизации YaMDb",
        message=f"Код авторизации:{confirmation_code}",
        from_email=None,
        recipient_list=[user.email])
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """Пользователь отправляет POST-запрос с параметрами username и
    confirmation_code на эндпоинт /api/v1/auth/token/, в ответе на
    запрос ему приходит token (JWT-токен).
    """

    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"])
    if default_token_generator.check_token(
            user, serializer.validated_data["confirmation_code"]):
        token = AccessToken().for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)

    @action(
        methods=[
            "get",
            "patch"],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer)
    def user_edit_get_own_profile(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
