import datetime as dt

from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.shortcuts import get_object_or_404
from django.db.models import Avg

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
    category = CategorySerilizer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)

    class Meta:
        model = Title
        fields = '__all__'

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
