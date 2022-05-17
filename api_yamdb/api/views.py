from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import EMAIL_HOST_USER
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import Admin, IsAdminOrReadOnly, ReviewCommentPermission
from .serializers import CategorySerilizer, CommentsSerializer
from .serializers import (GenreSerializer, PostTitleSerializer,
                          ReviewSerializer, TitleSerializer,
                          TokenConfirmationSerializer,
                          UserRegistrationSerializer, UserSerializer)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token)}


@api_view(['POST'])
def sign_up(request):
    def send_email(user):
        token = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Код подтверждения: {token}',
            EMAIL_HOST_USER,
            [user.email])

    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    try:
        user = User.objects.get_or_create(email=email, username=username)[0]
    except Exception:
        return Response(
            'Введено неверное имя пользователя или e-mail',
            status=status.HTTP_400_BAD_REQUEST)
    send_email(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_token(request):
    serializer = TokenConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        return Response(get_tokens_for_user(user))
    return Response(
        data='Неверный код подтверждения',
        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['username']
    permission_classes = [Admin]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerilizer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return PostTitleSerializer
        else:
            return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermission,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    permission_classes = (ReviewCommentPermission,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
