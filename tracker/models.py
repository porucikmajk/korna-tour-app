from django.db import models
from django.conf import settings

class POI(models.Model):
    CATEGORY_CHOICES = [
        ("priroda", "Príroda"),
        ("historia", "História"),
        ("turistika", "Turistika"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    distance_m = models.FloatField(default=0.0)
    steps_est = models.IntegerField(default=0)


class TrackPoint(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    t = models.DateTimeField(auto_now_add=True)
    lat = models.FloatField()
    lng = models.FloatField()


class Visit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)
