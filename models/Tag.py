from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=250, unique=True, default="")

    def __str__(self):
        return self.tag
