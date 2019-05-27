from django.db import models

from .Tag import Tag
from .Category import Category


class Image(models.Model):
    image_path = models.FilePathField()
    image_title = models.CharField(max_length=250)
    tags = models.ManyToManyField(Tag)
    categories = models.ManyToManyField(Category)
    creation_date = models.DateField('image created on')

    def __str__(self):
        return f"{self.image_title}: {self.image_path}"
