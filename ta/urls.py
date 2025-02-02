from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Home view
    path("home/", views.home_view, name="home"),
    # Routes and related functionality
    path("add-route/", views.add_route, name="add_route"),
    path(
        "add-route-links/<int:routeId>/", views.add_route_links, name="add_route_links"
    ),
    path("view-routes/", views.view_routes, name="view_routes"),
    path("add-route-stop/", views.add_route_stop, name="add_route_stop"),
    path(
        "generate_report/",
        views.generate_report,
        name="generate_report",
    ),
    path("search-route-stops/", views.search_route_stops, name="search_route_stops"),
]

# Set the login URL to match your custom login page
from django.conf import settings

if not hasattr(settings, "LOGIN_URL") or settings.LOGIN_URL == "/accounts/login/":
    settings.LOGIN_URL = "/login/"
