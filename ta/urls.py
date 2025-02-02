from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    # Home view
    path("home/", views.home_view, name="home"),
    # Routes and related functionality
    path("add-route/", views.add_route, name="add_route"),
    path(
        "add-route-links/<int:routeId>/", views.add_route_links, name="add_route_links"
    ),
    path(
        "remove-route-link/<int:routeLinkId>/<int:routeId>",
        views.remove_route_link,
        name="remove_route_link",
    ),
    path(
        "save-route-links/<int:routeId>/",
        views.save_route_links,
        name="save_route_links",
    ),
    path("view-routes/", views.view_routes, name="view_routes"),
    path("add-route-stop/", views.add_route_stop, name="add_route_stop"),
    path(
        "generate_report/",
        views.generate_report,
        name="generate_report",
    ),
]

# Set the login URL to match your custom login page
from django.conf import settings

if not hasattr(settings, "LOGIN_URL") or settings.LOGIN_URL == "/accounts/login/":
    settings.LOGIN_URL = "/login/"
