from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = ((USER, 'USER'), (MODERATOR, 'MODERATOR'), (ADMIN, 'ADMIN'))

    email = models.EmailField(max_length=254, unique=True, blank=False)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(max_length=300, choices=ROLES, default=ROLES[0][0])

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username


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
        ordering = ['-pub_date']
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

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text
