from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    # Home
    path("home/", views.home_view, name="home"),
    path("add-route/", views.add_route, name="add_route"),
    path("add-route-path/<int:routeId>/", views.add_route_path, name="add_route_path"),
    path(
        "remove-route-path/<int:routePathId>/<int:routeId>",
        views.remove_route_path,
        name="remove_route_path",
    ),
    path(
        "save-all-route-path/<int:routeId>/",
        views.save_all_route_path,
        name="save_all_route_path",
    ),
    path("view-routes/", views.view_routes, name="view_routes"),
    path("add-route-stop/", views.add_route_stop, name="add_route_stop"),
    path("add-route-link/", views.add_route_link, name="add_route_link"),
    path(
        "add-route-to-journey/<int:routeId>",
        views.add_route_to_journey,
        name="add_route_to_journey",
    ),
    path("generate_report/", views.generate_report, name="generate_report"),
]

# Set the login URL to match your custom login page
from django.conf import settings

if not hasattr(settings, "LOGIN_URL") or settings.LOGIN_URL == "/accounts/login/":
    settings.LOGIN_URL = "/login/"
