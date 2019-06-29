from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=250, unique=True, default="")

    def __str__(self):
        return self.tag

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        if other.tag == self.tag:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.tag)
