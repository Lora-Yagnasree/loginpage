from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.conf import settings

ROLE_TYPE = (
    ('Manager', "Manager"),
    ('HR', "HR"),
    ('Employee', "Employee")
)

class CustomUser(AbstractUser):
    username = None
    role = models.CharField(choices=ROLE_TYPE, max_length=100)
    employee_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=254, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.employee_id

    objects = UserManager()


class Attendance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_in_location = models.CharField(max_length=255, blank=True, null=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    clock_out_location = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def working_hours(self):
        if self.clock_in and self.clock_out:
            return round((self.clock_out - self.clock_in).total_seconds() / 3600, 2)
        return None

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"
