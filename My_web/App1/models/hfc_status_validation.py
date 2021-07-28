from django.db import models


class Hfc_Status_Validation(models.Model):
    LoB = models.CharField(max_length=100)
    Report_date = models.CharField(max_length=50)
    Flag = models.CharField(max_length=50)
