from django.db import models


class Bucket(models.Model):
    LD_limit = models.CharField(max_length=50)
    bucket = models.CharField(max_length=100)
    stage = models.CharField(max_length=50)

