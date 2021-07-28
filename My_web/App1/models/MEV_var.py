from django.db import models


class MevVar(models.Model):
    Micro_Economic_variable = models.CharField(max_length=200)
    Best_case = models.FloatField()
    Worst_case = models.FloatField()
    Reporting_date = models.CharField(max_length=100)
    LOB = models.CharField(max_length=100)
    Upload_date  = models.DateTimeField(primary_key=True)

