from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Trip, POI, Visit

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"

class POISerializer(serializers.ModelSerializer):
    class Meta:
        model = POI
        fields = "__all__"

class VisitSerializer(serializers.ModelSerializer):
    poi_id = serializers.IntegerField(source="poi.id")
    poi_name = serializers.CharField(source="poi.name")
    poi_category = serializers.CharField(source="poi.category")

    class Meta:
        model = Visit
        fields = ["poi_id", "poi_name", "poi_category", "visited_at"]
