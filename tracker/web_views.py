from .models import POI, Visit, Trip
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

## Admin + User Interface ##

@login_required
def profile_page(request):
    user = request.user

    total_trips = Trip.objects.filter(user=user).count()
    total_visits = Visit.objects.filter(user=user).count()

    ctx = {
        "u": user,
        "is_admin": user.is_staff or user.is_superuser,
        "total_trips": total_trips,
        "total_visits": total_visits,
    }
    return render(request, "profile.html", ctx)


@staff_member_required
def admin_panel_page(request):
    # len staff/superuser
    pois = POI.objects.all().order_by("category", "name")
    users = User.objects.all().order_by("username")

    return render(request, "admin_panel.html", {
        "pois": pois,
        "users": users,
    })

@csrf_protect
def register_page(request):
    return render(request, "register.html")

def activation_sent_page(request):
    return render(request, "activation_sent.html")

@require_http_methods(["POST"])
@csrf_protect
def register_submit(request):
    username = (request.POST.get("username") or "").strip()
    email = (request.POST.get("email") or "").strip()
    password = request.POST.get("password") or ""

    if not username or not email or not password:
        return render(request, "register.html", {"error": "Vyplň username, email a heslo."})

    if User.objects.filter(username=username).exists():
        return render(request, "register.html", {"error": "Toto používateľské meno už existuje."})

    if User.objects.filter(email=email).exists():
        return render(request, "register.html", {"error": "Tento email už je použitý."})

    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_active = False
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # link na aktiváciu
    activate_url = request.build_absolute_uri(f"/activate/{uid}/{token}/")

    subject = "Aktivácia účtu – Korňa"
    message = (
        f"Ahoj {user.username},\n\n"
        f"Klikni na tento link a aktivuj si účet:\n{activate_url}\n\n"
        f"Ak si sa neregistroval ty, ignoruj tento email."
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    return redirect("/activation-sent/")

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "activation_ok.html")
    else:
        return render(request, "activation_invalid.html")
