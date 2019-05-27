from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    creation_date = models.DateField('account created on')
    last_pass_change = models.DateField('password last changed on')

    def __str__(self):
        return self.username
