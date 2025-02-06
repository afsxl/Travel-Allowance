from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *


def login_view(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def home_view(request):
    routes = Route.objects.all()
    return render(request, "home.html", {"routes": routes})


@login_required
def view_routes(request):
    routes = Route.objects.all()
    routesWithPaths = []
    for route in routes:
        routePaths = RoutePath.objects.filter(route=route)
        routesWithPaths.append({"route": route, "routePaths": routePaths})
    return render(request, "view_routes.html", {"routesWithPaths": routesWithPaths})


@login_required
def add_route_stop(request):
    stopTypes = StopTypes.choices
    success = ""
    error = ""
    routeStopName = ""
    stopType = ""

    if request.method == "POST":

        routeStopName = request.POST.get("routeStopName")
        stopType = request.POST.get("stopType")

        print(type(stopType))

        if RouteStop.objects.filter(name=routeStopName).exists():
            error = f"Route stop {routeStopName} already exists!"
        else:
            RouteStop.objects.create(
                name=routeStopName,
                type=stopType,
                createdBy=request.user,
                verified=False,
            )
            routeStopName = ""
            stopType = ""
            success = "Stop added successfully"

    return render(
        request,
        "add_route_stop.html",
        {
            "routeStopName": routeStopName,
            "stopType": stopType,
            "stopTypes": stopTypes,
            "success": success,
            "error": error,
        },
    )


@login_required
def add_route(request):
    routeStops = RouteStop.objects.filter(
        Q(verified=True) | Q(createdBy=request.user)
    ).exclude(type=StopTypes.INTERMEDIATE_STOP)
    success = ""
    error = ""
    sourceId = ""
    destinationId = ""

    if request.method == "POST":
        sourceId = request.POST.get("source")
        destinationId = request.POST.get("destination")

        if sourceId and destinationId:
            if sourceId == destinationId:
                error = "Source and Destination are same"
            elif Route.objects.filter(
                source=sourceId, destination=destinationId
            ).exists():
                error = "This route already exists"
            else:
                source = RouteStop.objects.get(id=sourceId)
                destination = RouteStop.objects.get(id=destinationId)
                Route.objects.create(
                    source=source,
                    destination=destination,
                    createdBy=request.user,
                    verified=False,
                )
                success = "Route added successfully"
                sourceId = ""
                destinationId = ""

    return render(
        request,
        "add_route.html",
        {
            "route_stops": routeStops,
            "sourceId": sourceId,
            "destinationId": destinationId,
            "success": success,
            "error": error,
        },
    )


@login_required
def add_route_link(request):
    modes = ModesOfTravel.choices
    stops = RouteStop.objects.filter(Q(verified=True) | Q(createdBy=request.user))
    success = ""
    error = ""
    start = ""
    end = ""
    mode = ""
    distance = ""
    price = ""

    if request.method == "POST":
        start = request.POST.get("start")
        end = request.POST.get("end")
        mode = request.POST.get("mode")
        distance = request.POST.get("distance")
        price = request.POST.get("price")

        if start == end:
            error = "Start point and end point is same"
        elif float(distance) <= 0:
            error = "Invalid Distance"
        elif float(price) < 1:
            error = "Invalid Price"
        elif RouteLink.objects.filter(start=start, end=end).exists():
            error = "Route Link Already Exists"
        else:
            start = RouteStop.objects.get(id=start)
            end = RouteStop.objects.get(id=end)
            RouteLink.objects.create(
                start=start,
                end=end,
                mode=mode,
                distance=distance,
                price=price,
                verified=False,
                createdBy=request.user,
            )
            success = "Route Link Added Successfully"
            start = ""
            end = ""
            mode = ""
            distance = ""
            price = ""

    return render(
        request,
        "add_route_link.html",
        {
            "modes": modes,
            "stops": stops,
            "success": success,
            "error": error,
            "start": start,
            "end": end,
            "mode": mode,
            "distance": distance,
            "price": price,
        },
    )


@login_required
def add_route_path(request, routeId):
    route = Route.objects.get(id=routeId)
    routeLinks = RouteLink.objects.filter(Q(verified=True) | Q(createdBy=request.user))
    routePaths = RoutePath.objects.filter(route=routeId)

    return render(
        request,
        "add_route_path.html",
        {
            "route": route,
            "routeLinks": routeLinks,
        },
    )


@login_required
def remove_route_link(request, routeLinkId, routeId):
    route = Route.objects.get(id=routeId)
    last_stop = route.source
    stops = RouteStop.objects.all()
    modes = ModesOfTravel.choices
    if TemporaryRouteLink.objects.filter(id=routeLinkId).exists():
        TemporaryRouteLink.objects.filter(id=routeLinkId).delete()
    routeLinks = TemporaryRouteLink.objects.filter(route=route).order_by("order")
    if routeLinks.count():
        last_stop = routeLinks.last().end

    return render(
        request,
        "add_route_links.html",
        {
            "route": route,
            "stops": stops,
            "last_stop": last_stop,
            "modes": modes,
            "routeLinks": routeLinks,
        },
    )


def save_route_links(request, routeId):
    currentRoute = Route.objects.get(id=routeId)
    sameRoutes = Route.objects.filter(
        source=currentRoute.source, destination=currentRoute.destination
    ).exclude(id=routeId)

    temporaryRouteLinks = TemporaryRouteLink.objects.filter(route=routeId).order_by(
        "order"
    )

    for route in sameRoutes:
        routeLinks = RouteLink.objects.filter(route=route).order_by("order")
        if routeLinks.count() != temporaryRouteLinks.count():
            continue
        duplicate = True
        for routeLink, temporaryRouteLink in zip(routeLinks, temporaryRouteLinks):
            if (
                routeLink.start != temporaryRouteLink.start
                or routeLink.end != temporaryRouteLink.end
                or routeLink.distance != temporaryRouteLink.distance
                or routeLink.price != temporaryRouteLink.price
            ):
                duplicate = False
                break
        if duplicate:
            return render(
                request,
                "add_route_links.html",
                {
                    "route": route,
                    "stops": RouteStop.objects.all(),
                    "modes": ModesOfTravel.choices,
                    "routeLinks": temporaryRouteLinks,
                    "message": "Duplicate Route Exists",
                },
            )

    RouteLink.objects.filter(route=routeId).delete()
    for index, temporaryRouteLink in enumerate(temporaryRouteLinks):
        RouteLink.objects.create(
            route=temporaryRouteLink.route,
            start=temporaryRouteLink.start,
            end=temporaryRouteLink.end,
            mode=temporaryRouteLink.mode,
            distance=temporaryRouteLink.distance,
            price=temporaryRouteLink.price,
            order=index + 1,
        )

    TemporaryRouteLink.objects.filter(route=routeId).delete()
    return redirect("view_routes")


@login_required
def generate_report(request):
    routes = Route.objects.all()
    return render(request, "generate_report.html", {"routes": routes})
