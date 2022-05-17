import datetime as dt

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comments, Genre, Review, Title, User


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        """Ник (me) запрещен."""
        if value == 'me':
            raise serializers.ValidationError('Логин недоступен')
        return value


class TokenConfirmationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class ConfirmationCodeSerializer(serializers.Serializer):
    """Код подтверждения на почту после регистрации."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User
        read_only_fields = ('role',)


class CategorySerilizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов."""

    category = CategorySerilizer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField(source='rating')

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        """Получение рейтинга произведения, при его наличии."""
        rating = obj.reviews.all().aggregate(Avg('score')).get('score__avg')
        if rating:
            return int(rating)


class PostTitleSerializer(TitleSerializer):
    """Сериализатор для POST и UPDATE запросов."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )

    def validate_year(self, value):
        """Валидатор года выхода произведения."""
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год издания!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)

    def validate_score(self, value):
        """Проверяем, что значение score от 1 до 10."""
        if 1 > value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10. '
                f'Было передано значение score={value}'
            )
        return value

    def validate(self, data):
        """Проверяем уникальность отзыва."""
        is_post_request = 'POST' in str(self.context['request'])
        if not is_post_request:
            return data

        author = self.context['request'].user
        title_id = self.context['view'].kwargs['title_id']
        review_exists = Review.objects.filter(author=author,
                                              title_id=title_id).exists()
        if review_exists:
            raise serializers.ValidationError(
                'Пользователь уже отправлял отзыв на это произведение.'
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ('review',)
