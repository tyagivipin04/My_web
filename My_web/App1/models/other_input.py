from django.db import models


class OtherInput(models.Model):
    variable = models.CharField(max_length=200)
    input = models.FloatField()
    Reporting_date = models.CharField(max_length=100)
    LOB = models.CharField(max_length=100)
    Upload_date  = models.DateTimeField(primary_key=True)

