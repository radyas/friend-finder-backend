import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from files.models import File


class Roles(models.TextChoices):
    # User Roles
    SUPER_ADMIN = 'SUPER_ADMIN', _('SUPER_ADMIN')
    HR = 'HR', _('HR')
    EMPLOYEE = 'EMPLOYEE', _('EMPLOYEE')


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE
    )
    profile_picture = models.ForeignKey(File, related_name='owners', on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def is_super_admin(self):
        return self.role == Roles.SUPER_ADMIN or self.is_superuser

    def is_admin_user(self):
        return self.role in [Roles.HR, Roles.SUPER_ADMIN]

    def is_user(self):
        return self.role == Roles.EMPLOYEE
