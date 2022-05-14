from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator




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

        
class Category(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(max_length=256)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        related_name='genre',
        on_delete=models.SET_NULL,
        null=True,
        )

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('текст отзыва')
    pub_date = models.DateTimeField(
        'дата отправки отзыва',
        auto_now_add=True
    )
    score = models.PositiveSmallIntegerField(
        'оценка по 10-ти бальной шкале',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='пользователь, оставляющий отзыв',
        )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='review_is_unique'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    text = models.TextField('текст комментария')
    pub_date = models.DateTimeField(
        'дата отправки комментария',
        auto_now_add=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарии отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пользователь, оставляющий комментарий',
    )

    def __str__(self):
        return self.text
      