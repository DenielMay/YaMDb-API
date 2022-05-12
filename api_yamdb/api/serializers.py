from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Проверить ник и почту на уникальность при регистрации"""

    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    def validate_username(self, value):
        """Ник (me) запрещен"""
        if value == "me":
            raise serializers.ValidationError("Логин недоступен")
        return value

    class Meta:
        fields = ("username", "email")
        model = User


class ConfirmationCodeSerializer(serializers.Serializer):
    """Код подтверждения на почту после регистрации"""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        model = User
        read_only_fields = ('role',)
