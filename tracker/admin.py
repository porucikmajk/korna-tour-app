from django.contrib import admin
from .models import POI, Trip, TrackPoint, Visit

admin.site.register(POI)
admin.site.register(Trip)
admin.site.register(TrackPoint)
admin.site.register(Visit)