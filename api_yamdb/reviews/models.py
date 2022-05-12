from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')]
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=True,
        unique=True)
    email = models.EmailField(
        verbose_name='E-mail пользователя',
        unique=True,
        max_length=254)
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=150,
        choices=ROLES,
        default=USER)
    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='Такой пользователь уже есть')]
        ordering = ['id']

