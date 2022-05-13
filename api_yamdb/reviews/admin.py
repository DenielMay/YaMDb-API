from django.contrib import admin
from .models import User, Category, Genre, Title, Review, Comments


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comments)
