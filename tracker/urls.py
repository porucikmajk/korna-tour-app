from django.urls import path
from . import api_views
from tracker import web_views

urlpatterns = [
    path("register/", api_views.register),
    path("login/", api_views.login_api),

    path("pois/", api_views.pois),

    path("trip/start/", api_views.start_trip),
    path("trip/stop/", api_views.stop_trip),
    path("trip/active/", api_views.active_trip),
    path("trip/<int:trip_id>/track/", api_views.track_point),

    path("stats/", api_views.stats),

    path("profile/", web_views.profile_page),
    path("admin-panel/", web_views.admin_panel_page),

    # admin API
    path("admin/poi/create/", api_views.admin_poi_create),
    path("admin/poi/<int:poi_id>/update/", api_views.admin_poi_update),
    path("admin/poi/<int:poi_id>/delete/", api_views.admin_poi_delete),
    path("admin/user/<int:user_id>/delete/", api_views.admin_user_delete),

    ## TEMP ##
    path("bootstrap-admin/", api_views.bootstrap_admin),
]
