from django.contrib import admin
from jester.models import Joke, Rating, Rater

admin.site.register(Joke)
admin.site.register(Rating)
admin.site.register(Rater)