from django.contrib import admin
from recommender.models import Joke, Rating, User

admin.site.register(Joke)
admin.site.register(Rating)
admin.site.register(User)

