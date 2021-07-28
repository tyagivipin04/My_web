from django.db import models


class LOB(models.Model):
    options = models.CharField(max_length=100)

    def __str__(self):
        return self.options

