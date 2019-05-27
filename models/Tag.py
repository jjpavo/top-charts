from django.db import models


class Tag(models.Model):
    tags = models.CharField(max_length=250)

    def __str__(self):
        return self.tags
