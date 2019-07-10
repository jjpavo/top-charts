from django.contrib.postgres.fields import JSONField
from django.db import models

from .User import User


class Chart(models.Model):
    chart = JSONField()
    name = models.CharField(max_length=250)
    creation_date = models.DateField('chart created on')
    modification_date = models.DateField('chart last modified on')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username}: {self.name}"
