from django.db import models
from django.contrib.auth.models import User
from .role import Role
from .lob_opt import LOB


class UserRole(models.Model):
    UserId = models.ForeignKey(User,on_delete=models.CASCADE)
    RoleId = models.ForeignKey(LOB,on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.RoleId