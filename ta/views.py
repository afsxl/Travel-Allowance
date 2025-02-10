from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime, date, time


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
            return redirect("view_profile")
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


def view_profile(request):
    success = ""
    if request.method == "POST":
        firstName = request.POST.get("first_name")
        lastName = request.POST.get("last_name")
        designation = request.POST.get("designation")
        basicPay = request.POST.get("basic_pay")
        accountNumber = request.POST.get("account_number")
        ifscCode = request.POST.get("ifsc_code")
        bankName = request.POST.get("bank_name")
        branchName = request.POST.get("branch_name")

        User.objects.filter(id=request.user.id).update(
            first_name=firstName, last_name=lastName
        )

        UserDetails.objects.update_or_create(
            user=request.user,
            defaults={
                "designation": designation,
                "basicPay": basicPay,
                "accountNumber": accountNumber,
                "ifscCode": ifscCode,
                "bankName": bankName,
                "branchName": branchName,
            },
        )
        success = "Profile updated successfully"
   
    userDetails = UserDetails.objects.filter(user=request.user).first()
    profile = {

        "firstName":  User.objects.get(id = request.user.id).first_name,
        "lastName": User.objects.get(id = request.user.id).last_name,
    }
    if userDetails:
        profile.update(
            {
                "designation": userDetails.designation,
                "basicPay": userDetails.basicPay,
                "accountNumber": userDetails.accountNumber,
                "ifscCode": userDetails.ifscCode,
                "bankName": userDetails.bankName,
                "branchName": userDetails.branchName,
            }
        )

    return render(request, "user_profile.html", {"profile": profile,"success":success})


@login_required
def view_routes(request):
    routes = Route.objects.filter(Q(verified=True) | Q(createdBy=request.user))
    routesWithPaths = []
    for route in routes:
        routePaths = RoutePath.objects.filter(route=route).order_by("order")
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

        if RouteStop.objects.filter(
            Q(name=routeStopName) & (Q(verified=True) | Q(createdBy=request.user))
        ).exists():
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
                Q(source=sourceId)
                & Q(destination=destinationId)
                & (Q(verified=True) | Q(createdBy=request.user))
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
        elif RouteLink.objects.filter(
            Q(start=start) & Q(end=end) & (Q(verified=True) | Q(createdBy=request.user))
        ).exists():
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
    routePaths = RoutePath.objects.filter(route=routeId).order_by("order")

    if request.method == "POST":
        routeLinkId = request.POST.get("routeLinkId")
        routeLink = RouteLink.objects.get(id=routeLinkId)
        TemporaryRoutePath.objects.create(
            route=route,
            routeLink=routeLink,
            order=1 if routePaths.count() == 0 else routePaths.last().order + 1,
            createdBy=request.user,
        )
    else:
        TemporaryRoutePath.objects.filter(
            route=routeId, createdBy=request.user
        ).delete()
        for routePath in routePaths:
            TemporaryRoutePath.objects.create(
                route=routePath.route,
                routeLink=routePath.routeLink,
                order=routePath.order,
                createdBy=request.user,
            )

    routePaths = TemporaryRoutePath.objects.filter(route=routeId).order_by("order")

    return render(
        request,
        "add_route_path.html",
        {"route": route, "routeLinks": routeLinks, "routePaths": routePaths},
    )


@login_required
def remove_route_path(request, routePathId, routeId):
    route = Route.objects.get(id=routeId)
    routeLinks = RouteLink.objects.filter(Q(verified=True) | Q(createdBy=request.user))
    routePaths = TemporaryRoutePath.objects.filter(route=routeId).order_by("order")

    if TemporaryRoutePath.objects.filter(id=routePathId).exists():
        TemporaryRoutePath.objects.filter(id=routePathId).delete()

    return render(
        request,
        "add_route_path.html",
        {"route": route, "routeLinks": routeLinks, "routePaths": routePaths},
    )


@login_required
def save_all_route_path(request, routeId):
    route = Route.objects.get(id=routeId)

    RoutePath.objects.filter(route=route, createdBy=request.user).delete()

    temporaryRoutePaths = TemporaryRoutePath.objects.filter(
        route=route, createdBy=request.user
    ).order_by("order")

    for index, temporaryRoutePath in enumerate(temporaryRoutePaths):
        RoutePath.objects.create(
            route=temporaryRoutePath.route,
            routeLink=temporaryRoutePath.routeLink,
            createdBy=request.user,
            order=index + 1,
        )

    TemporaryRoutePath.objects.filter(route=route, createdBy=request.user).delete()
    return redirect("view_routes")


@login_required
def add_route_to_journey(request, routeId):
    route = Route.objects.get(id=routeId)
    routePaths = RoutePath.objects.filter(route=route)
    error = ""
    journeyTime = {}

    if request.method == "POST":
        purpose = request.POST.get("purpose")
        previousRoute = None
        for routePath in routePaths:
            startDate = request.POST.get(f"startDate{routePath.id}")
            startTime = request.POST.get(f"startTime{routePath.id}")
            endDate = request.POST.get(f"endDate{routePath.id}")
            endTime = request.POST.get(f"endTime{routePath.id}")

            if startDate and startTime and endDate and endTime:
                start_datetime = datetime.strptime(
                    f"{startDate} {startTime}", "%Y-%m-%d %H:%M"
                )
                end_datetime = datetime.strptime(
                    f"{endDate} {endTime}", "%Y-%m-%d %H:%M"
                )

                if (
                    previousRoute
                    and journeyTime.get(f"end_datetime{previousRoute.id}")
                    > start_datetime
                ) or (start_datetime > end_datetime):
                    print("Error")
                    error = f"Invalid Date selected for {routePath.routeLink.start.name} To {routePath.routeLink.end.name}"
                else:
                    journeyTime[f"start_datetime{routePath.id}"] = start_datetime
                    journeyTime[f"end_datetime{routePath.id}"] = end_datetime

            previousRoute = routePath

        if not error:
            journeyRoute = JourneyRoute.objects.create(
                purpose=purpose,
                source=route.source.name,
                destination=route.destination.name,
                user=request.user,
            )
            for routePath in routePaths:
                journeyRouteLink = JourneyRouteLink.objects.create(
                    start=routePath.routeLink.start.name,
                    end=routePath.routeLink.end.name,
                    mode=ModesOfTravel(routePath.routeLink.mode).label,
                    distance=routePath.routeLink.distance,
                    price=routePath.routeLink.price,
                    user=request.user,
                )
                JourneyRoutePath.objects.create(
                    route=journeyRoute,
                    routeLink=journeyRouteLink,
                    order=routePath.order,
                    startDate=journeyTime.get(f"start_datetime{routePath.id}").date(),
                    startTime=journeyTime.get(f"start_datetime{routePath.id}").time(),
                    endDate=journeyTime.get(f"end_datetime{routePath.id}").date(),
                    endTime=journeyTime.get(f"end_datetime{routePath.id}").time(),
                    user=request.user,
                )

            return redirect("view_journeys")

    return render(
        request,
        "add_journey.html",
        {
            "route": route,
            "routePaths": routePaths,
            "error": error,
        },
    )


@login_required
def view_journeys(request):
    journeyRoutes = JourneyRoute.objects.filter(user=request.user)
    journeyRoutesWithPaths = []
    for journeyRoute in journeyRoutes:
        journeyRoutePaths = JourneyRoutePath.objects.filter(
            route=journeyRoute
        ).order_by("order")
        journeyRoutesWithPaths.append(
            {"journeyRoute": journeyRoute, "journeyRoutePaths": journeyRoutePaths}
        )
    return render(
        request,
        "view_journeys.html",
        {"journeyRoutesWithPaths": journeyRoutesWithPaths},
    )


@login_required
def generate_report(request, journeyRouteId):
    profile = UserDetails.objects.filter(user=request.user).first()
    if not profile:
        return redirect("view_profile")
    journeyRoute = JourneyRoute.objects.get(id=journeyRouteId)
    journeyRoutePaths = JourneyRoutePath.objects.filter(route=journeyRoute)
    return render(
        request,
        "generate_report.html",
        {
            "profile": profile,
            "journeyRoute": journeyRoute,
            "journeyRoutePaths": journeyRoutePaths,
            "total_count":len(journeyRoutePaths) 
        },
    )
