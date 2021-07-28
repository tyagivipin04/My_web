from django.db import models


class Mev(models.Model):
    Year = models.IntegerField()
    GDP = models.IntegerField()
    Inflation = models.IntegerField()
    Interest_rate = models.IntegerField()
    Domestic_credit_growth = models.IntegerField()
    Dummy_var = models.IntegerField()
    Reporting_date = models.CharField(max_length=100)
    LOB = models.CharField(max_length=100)
    Upload_date = models.DateTimeField(primary_key=True)
