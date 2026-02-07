"""
URL configuration for korna_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tracker import api_views
from tracker import web_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tracker.urls")),
    path("", api_views.login_page),
    path("dashboard/", api_views.dashboard_page),
    path("map/", api_views.map_page),
    path("register/", web_views.register_page),
    path("register/submit/", web_views.register_submit),
    path("activate/<uidb64>/<token>/", web_views.activate_account, name="activate"),
    path("activation-sent/", web_views.activation_sent_page),
    path("profile/", web_views.profile_page),
    path("admin-panel/", web_views.admin_panel_page),

]