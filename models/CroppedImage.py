from django.db import models

from .Image import Image


class CroppedImage(models.Model):
    image_path = models.FilePathField(max_length=4096)
    creation_date = models.DateField('image created on')
    parent_image = models.ForeignKey(Image, on_delete=models.CASCADE)

    def __str__(self):
        return f"Parent: {self.parent_image}, Path: {self.image_path}"
