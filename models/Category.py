from django.db import models


class Category(models.Model):
    FILM = 'FILM'
    FOOD = 'FOOD'
    TEAM = 'TEAM'
    SPORT = 'SPORT'
    SONG = 'SONG'
    ALBUM = 'ALBUM'
    COUNTRY = 'COUNTRY'
    CITY = 'CITY'
    REGION = 'REGION'
    LANGUAGE = 'LANGUAGE'
    PERSON = 'PERSON'

    CATEGORY_CHOICES = [
        (FILM, 'Film'),
        (FOOD, 'Food'),
        (TEAM, 'Team'),
        (SPORT, 'Sport'),
        (SONG, 'Song'),
        (ALBUM, 'Album'),
        (COUNTRY, 'Country'),
        (CITY, 'City'),
        (REGION, 'Region'),
        (LANGUAGE, 'Language'),
        (PERSON, 'Person'),
    ]

    categories = models.CharField(
        max_length=250,
        choices=CATEGORY_CHOICES,
        default=FILM,
    )

    def __str__(self):
        return self.categories
