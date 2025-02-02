from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse


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
def add_route_stop(request):
    routeStopName = ""
    message = ""
    stopTypes = StopTypes.choices

    if request.method == "POST":
        routeStopName = request.POST.get("routeStopName")
        stopType = request.POST.get("stopType")
        if RouteStop.objects.filter(name=routeStopName).exists():
            message = f"Route stop {routeStopName} already exists!"
        else:
            RouteStop.objects.create(name=routeStopName, stopType=stopType).save()
            return redirect("add_route_stop")
    return render(
        request,
        "add_route_stop.html",
        {"routeStopName": routeStopName, "message": message, "stopTypes": stopTypes},
    )


@login_required
def add_route(request):
    routeStops = RouteStop.objects.exclude(stopType=StopTypes.INTERMEDIATE_STOP)

    if request.method == "POST":
        sourceId = request.POST.get("source")
        destinationId = request.POST.get("destination")

        if sourceId and destinationId:
            if sourceId == destinationId:
                return render(
                    request,
                    "add_route.html",
                    {
                        "route_stops": routeStops,
                        "message": "Source and Destination are same",
                        "sourceId": sourceId,
                        "destinationId": destinationId,
                    },
                )
            source = RouteStop.objects.get(id=sourceId)
            destination = RouteStop.objects.get(id=destinationId)

            Route.objects.create(
                source=source,
                destination=destination,
            )

            return render(
                request,
                "add_route.html",
                {"route_stops": routeStops, "message": "Route added successfully"},
            )
    return render(request, "add_route.html", {"route_stops": routeStops})


@login_required
def add_route_links(request, routeId):
    route = Route.objects.get(id=routeId)
    stops = RouteStop.objects.all()
    last_stop = route.source
    modes = ModesOfTravel.choices

    if request.method == "POST":
        startId = request.POST.get("start")
        endId = request.POST.get("end")
        mode = request.POST.get("mode")
        distance = request.POST.get("distance")
        price = request.POST.get("price")

        order = (
            1
            if TemporaryRouteLink.objects.filter(route=routeId).order_by("order").last()
            == None
            else TemporaryRouteLink.objects.filter(route=routeId)
            .order_by("order")
            .last()
            .order
            + 1
        )

        start = RouteStop.objects.get(id=startId)
        end = RouteStop.objects.get(id=endId)
        distance = float(distance)
        price = float(price)
        TemporaryRouteLink.objects.create(
            route=route,
            start=start,
            end=end,
            mode=mode,
            distance=distance,
            price=price,
            order=order,
        )

        routeLinks = TemporaryRouteLink.objects.filter(route=routeId).order_by("order")
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

    TemporaryRouteLink.objects.filter(route=routeId).delete()
    routeLinks = RouteLink.objects.filter(route=routeId).order_by("order")
    for routeLink in routeLinks:
        TemporaryRouteLink.objects.create(
            route=routeLink.route,
            start=routeLink.start,
            end=routeLink.end,
            mode=routeLink.mode,
            distance=routeLink.distance,
            price=routeLink.price,
            order=routeLink.order,
        )
    routeLinks = TemporaryRouteLink.objects.filter(route=routeId).order_by("order")

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


@login_required
def remove_route_link(request, routeLinkId):
    route = TemporaryRouteLink.objects.filter(id=routeLinkId).last().route
    stops = RouteStop.objects.all()
    modes = ModesOfTravel.choices
    TemporaryRouteLink.objects.filter(id=routeLinkId).delete()
    routeLinks = TemporaryRouteLink.objects.filter(route=route).order_by("order")

    return render(
        request,
        "add_route_links.html",
        {
            "route": route,
            "stops": stops,
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
def view_routes(request):
    routes = Route.objects.all()
    routesWithLinks = []
    for route in routes:
        routeLinks = RouteLink.objects.filter(route=route)
        routesWithLinks.append({"route": route, "routeLinks": routeLinks})
    return render(request, "view_routes.html", {"routesWithLinks": routesWithLinks})


@login_required
def search_route_stops(request):
    if request.method == "GET" and "query" in request.GET:
        query = request.GET.get("query", "")
        results = RouteStop.objects.filter(name__icontains=query).values("id", "name")
        return JsonResponse(list(results), safe=False)
    return JsonResponse([], safe=False)


@login_required
def generate_report(request):
    routes = Route.objects.all()
    return render(request, "generate_report.html", {"routes": routes})
