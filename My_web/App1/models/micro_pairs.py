from django.db import models


class MicroPair(models.Model):
    Pair = models.CharField(max_length=100)
    Variable_1 = models.CharField(max_length=100)
    Variable_2 = models.CharField(max_length=100)
    Reporting_date = models.CharField(max_length=100)
    LOB = models.CharField(max_length=100)
    Upload_date = models.DateTimeField(primary_key=True)
