from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    ROLES = [
        ('user', 'пользователь'),
        ('moderator', 'модератор'),
        ('admin', 'администратор'),
    ]
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Права доступа',
        max_length=20,
        choices=ROLES,
        default='user',
    )


class Category(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    # TODO: доделать rating
    rating = 10  # взять из отзывов
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        )

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField('текст отзыва')
    pub_date = models.DateTimeField(
        'дата отправки отзыва',
        auto_now_add=True,
        db_index=True,
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
        auto_now_add=True,
        db_index=True,
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
