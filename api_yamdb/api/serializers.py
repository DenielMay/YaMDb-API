import datetime as dt
from django.db.models import Avg

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import User, Category, Genre, Title, Review, Comments


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
    category = serializers.SlugRelatedField(
        slug_field='name', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='name', queryset=Genre.objects.all(), many=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        rating = obj.reviews.all().aggregate(Avg('score'))
        rating = int(rating.get('score__avg'))
        return rating

    def validate_year(self, value):
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
        if 1 > value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10. '
                f'Было передано значение score={value}'
            )
        return value


class CommentsSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ('review',)
