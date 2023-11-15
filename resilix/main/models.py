from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class AlertChoices(models.IntegerChoices):
    Volcanic_eruption = 1
    Flood = 2
    Fire = 3
    Health_Emergency = 4
    Others = 5


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()


class Alert(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    alert_type = models.PositiveSmallIntegerField(
        choices=AlertChoices.choices, default=AlertChoices.Flood
    )
    date_time_of_alert = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=None)
    description = models.TextField()


class DisasterFeedback(models.Model):
    description = models.TextField()
    date_time_of_alert = models.DateTimeField(auto_now_add=True)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
