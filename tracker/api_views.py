import math
from django.db.models import F
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Trip, TrackPoint, POI, Visit
from .serializers import TripSerializer, VisitSerializer
from .serializers import POISerializer, TripSerializer

STEP_LEN = 0.78
VISIT_RADIUS = 30

## TEMP ##
import os
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def bootstrap_admin(request):
    key = request.query_params.get("key", "")
    if key != os.environ.get("BOOTSTRAP_KEY", ""):
        return Response({"error": "forbidden"}, status=403)

    username = os.environ.get("BOOTSTRAP_ADMIN_USER", "admin")
    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "")
    password = os.environ.get("BOOTSTRAP_ADMIN_PASS", "admin12345")

    u, created = User.objects.get_or_create(username=username, defaults={"email": email})
    u.email = email or u.email
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.set_password(password)   # nastavíme vždy
    u.save()

    return Response({"ok": True, "created": created, "username": username})







def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def login_page(request):
    return render(request, "login.html")

def dashboard_page(request):
    return render(request, "dashboard.html")

def map_page(request):
    return render(request, "map.html")

## Admin Interface ##
@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_poi_create(request):
    p = POI.objects.create(
        name=request.data.get("name","").strip(),
        description=request.data.get("description","").strip(),
        category=request.data.get("category","").strip(),
        lat=float(request.data.get("lat")),
        lng=float(request.data.get("lng")),
    )
    return Response({"ok": True, "id": p.id})


@api_view(["PUT"])
@permission_classes([IsAdminUser])
def admin_poi_update(request, poi_id):
    poi = POI.objects.get(id=poi_id)
    poi.name = request.data.get("name", poi.name).strip()
    poi.description = request.data.get("description", poi.description).strip()
    poi.category = request.data.get("category", poi.category).strip()
    poi.lat = float(request.data.get("lat", poi.lat))
    poi.lng = float(request.data.get("lng", poi.lng))
    poi.save()
    return Response({"ok": True})


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_poi_delete(request, poi_id):
    POI.objects.filter(id=poi_id).delete()
    return Response({"ok": True})


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_user_delete(request, user_id):
    if request.user.id == user_id:
        return Response({"error": "Nemôžeš zmazať sám seba."}, status=400)

    User.objects.filter(id=user_id).delete()
    return Response({"ok": True})
## ##

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response({"error": "Chýba username alebo password"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Používateľské meno už existuje"}, status=409)

    User.objects.create_user(username=username, password=password)
    return Response({"ok": True})

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Chýba username alebo password"}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Nesprávne meno alebo heslo"}, status=400)

    # 🔐 DÔLEŽITÉ – kontrola aktivácie účtu
    if not user.is_active:
        return Response(
            {"error": "Účet nie je aktivovaný. Skontroluj email a klikni na aktivačný link."},
            status=403
        )

    login(request, user)
    return Response({"ok": True})

@api_view(["POST"])
def start_trip(request):
    Trip.objects.filter(user=request.user, ended_at__isnull=True).update(ended_at=timezone.now())
    trip = Trip.objects.create(user=request.user)
    return Response(TripSerializer(trip).data)

@api_view(["GET"])
def active_trip(request):
    trip = Trip.objects.filter(user=request.user, ended_at__isnull=True).order_by("-id").first()
    return Response({"trip": TripSerializer(trip).data if trip else None})


@api_view(["POST"])
def stop_trip(request):
    trip = Trip.objects.filter(user=request.user, ended_at__isnull=True).order_by("-id").first()
    if not trip:
        return Response({"error": "No active trip"}, status=404)
    trip.ended_at = timezone.now()
    trip.save()
    return Response({"trip": TripSerializer(trip).data})


@api_view(["POST"])
def track_point(request, trip_id):
    trip = Trip.objects.filter(id=trip_id, user=request.user, ended_at__isnull=True).first()
    if not trip:
        return Response({"error": "Trip not found/active"}, status=404)

    lat = float(request.data["lat"])
    lng = float(request.data["lng"])

    last = TrackPoint.objects.filter(trip=trip).last()
    TrackPoint.objects.create(trip=trip, lat=lat, lng=lng)

    if last:
        dist = haversine(last.lat, last.lng, lat, lng)
        trip.distance_m += dist
        trip.steps_est = int(trip.distance_m / STEP_LEN)
        trip.save()

    for poi in POI.objects.all():
        d = haversine(lat, lng, poi.lat, poi.lng)
        if d <= VISIT_RADIUS:
            Visit.objects.get_or_create(user=request.user, trip=trip, poi=poi)

    return Response({
        "distance_m": trip.distance_m,
        "steps_est": trip.steps_est
    })

@api_view(["GET"])
def stats(request):
    visits_qs = Visit.objects.filter(user=request.user).order_by("-visited_at")
    visits = VisitSerializer(visits_qs, many=True).data

    visited_poi_ids = list(
        visits_qs.values_list("poi_id", flat=True).distinct()
    )

    return Response({
        "visits": visits,
        "visited_poi_ids": visited_poi_ids,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def pois(request):
    data = POI.objects.all().order_by("name")
    return Response({"pois": POISerializer(data, many=True).data})
