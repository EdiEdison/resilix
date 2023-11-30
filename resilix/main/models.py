from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


import pyotp


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    otp = models.CharField(max_length=100, null=True, blank=True, unique=True)

    # validate opt
    def authenticate(self, otp):
        """This method authenticates the given otp"""
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False
        # Here we are using Time Based OTP. The interval is 300 seconds.
        # otp must be provided within this interval or it's invalid
        t = pyotp.TOTP(self.otp, interval=300)
        return t.verify(provided_otp)

    def __str__(self):
        return self.username


class AlertChoices(models.Model):
    emergency_name = models.CharField(
        max_length=25, blank=True, null=True, default=None
    )

    def __str__(self):
        return str(self.emergency_name)


class Location(models.Model):
    longitude = models.FloatField(default=None, blank=True, null=True)
    latitude = models.FloatField(default=None, blank=True, null=True)

    def __str__(self):
        return str(self.longitude)


class Alert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alert_type = models.ForeignKey(AlertChoices, on_delete=models.CASCADE, default=None)
    date_time_of_alert = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=None)
    description = models.TextField()
    first_aid_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class DisasterFeedback(models.Model):
    description = models.TextField()
    date_time_of_feedback = models.DateTimeField(auto_now_add=True)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)

    def __str__(self):
        return self.description[:30]
