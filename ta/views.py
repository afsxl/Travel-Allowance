from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
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
            ).save()

            return render(
                request,
                "add_route.html",
                {"route_stops": routeStops, "message": "Route added successfully"},
            )
    return render(request, "add_route.html", {"route_stops": routeStops})


@login_required
def select_route_for_link(request):
    routes = Route.objects.all()
    return render(request, "select_route_for_link.html", {"routes": routes})


@login_required
def add_route_links(request, routeId):
    route = Route.objects.get(id=routeId)
    stops = RouteStop.objects.all()
    last_stop = route.source
    modes = RouteLink.MODE_CHOICES

    last_link = RouteLink.objects.filter(route=route).order_by("-id").first()
    if last_link:
        last_stop = last_link.end

    if request.method == "POST":
        start_id = request.POST.get("start")
        end_id = request.POST.get("end")
        mode = request.POST.get("mode")
        distance = request.POST.get("distance")
        price = request.POST.get("price")

        try:
            start = RouteStop.objects.get(id=start_id)
            end = RouteStop.objects.get(id=end_id)
            distance = float(distance)
            price = float(price)

            RouteLink.objects.create(
                route=route,
                start=start,
                end=end,
                mode=mode,
                distance=distance,
                price=price,
            )
            messages.success(request, "Route link added successfully!")
            return redirect("add_route_links", id=route.id)

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(
        request,
        "add_route_links.html",
        {
            "route": route,
            "stops": stops,
            "last_stop": last_stop,
            "modes": modes,
        },
    )


@login_required
def add_route_path(request, route_id):
    route = get_object_or_404(Route, id=route_id)

    source = route.source
    destination = route.destination
    intermediate_links = RouteLink.objects.filter(route=route).order_by("id")

    max_order = (
        RoutePath.objects.filter(route=route).aggregate(Max("order"))["order__max"] or 0
    )
    next_order = max_order + 1

    try:
        route_path = RoutePath.objects.create(
            route=route,
            source=source,
            destination=destination,
            order=next_order,
        )

        route_path.route_links.set(intermediate_links)
        route_path.save()

        messages.success(request, "Route path added successfully!")
        return redirect("view_routes")

    except Exception as e:
        messages.error(request, f"An error occurred while saving the route path: {e}")
        return redirect("view_routes")


@login_required
def view_routes(request):
    routes = Route.objects.all()
    return render(request, "view_routes.html", {"routes": routes})


@login_required
def search_route_stops(request):
    if request.method == "GET" and "query" in request.GET:
        query = request.GET.get("query", "")
        results = RouteStop.objects.filter(name__icontains=query).values("id", "name")
        return JsonResponse(list(results), safe=False)
    return JsonResponse([], safe=False)
