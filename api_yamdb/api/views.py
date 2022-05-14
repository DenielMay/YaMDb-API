from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, permissions, mixins, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .permissions import Admin, AdminModeratorOwner, SafeMethods
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import User, Category, Genre, Title, Review, Comments
from .serializers import (
    CategorySerilizer, GenreSerializer, TitleSerializer,
    ReviewSerializer, CommentsSerializer, RegistrationSerializer, 
    ConfirmationCodeSerializer, UserSerializer, UserEditSerializer)
from .permissions import Admin



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


class ListCreateDestroyViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerilizer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [Admin | SafeMethods]



class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [Admin | SafeMethods]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('category', 'genre', 'name', 'year')
    permission_classes = [Admin | SafeMethods]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [AdminModeratorOwner | SafeMethods]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = [AdminModeratorOwner | SafeMethods]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return Comments.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
