from django.contrib import admin
from jester.models import Joke, Rating, User

admin.site.register(Joke)
admin.site.register(Rating)
admin.site.register(User)