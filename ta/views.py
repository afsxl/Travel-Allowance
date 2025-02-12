from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime, date, time
import inflect


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
    return render(request, "home.html")


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
        collegeName = request.POST.get("college_name")
        collegeDistrict = request.POST.get("college_district")
        address = request.POST.get("address")

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
                "collegeName": collegeName,
                "collegeDistrict": collegeDistrict,
                "address": address,
            },
        )
        success = "Profile updated successfully"

    userDetails = UserDetails.objects.filter(user=request.user).first()
    profile = {
        "firstName": User.objects.get(id=request.user.id).first_name,
        "lastName": User.objects.get(id=request.user.id).last_name,
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
                "collegeName": userDetails.collegeName,
                "collegeDistrict": userDetails.collegeDistrict,
                "address": userDetails.address,
            }
        )

    return render(
        request, "user_profile.html", {"profile": profile, "success": success}
    )


@login_required
def view_routes(request):
    routeStops = RouteStop.objects.filter(
        Q(verified=True) | Q(createdBy=request.user)
    ).exclude(type=StopTypes.INTERMEDIATE_STOP)
    routes = Route.objects.filter(Q(verified=True) | Q(createdBy=request.user))

    routesWithPaths = []

    if request.method == "POST":
        sourceId = request.POST.get("source")
        destinationId = request.POST.get("destination")
        if sourceId and destinationId:
            routes = routes.filter(source=sourceId, destination=destinationId)
        else:
            routes = []

    for route in routes:
        routePaths = RoutePath.objects.filter(route=route).order_by("order")
        routesWithPaths.append({"route": route, "routePaths": routePaths})
    return render(
        request,
        "view_routes.html",
        {"routesWithPaths": routesWithPaths, "stops": routeStops},
    )


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
    error = ""

    if request.method == "POST":
        routeLinkId = request.POST.get("routeLinkId")
        routeLink = RouteLink.objects.get(id=routeLinkId)
        temporaryRoutePaths = TemporaryRoutePath.objects.filter(route=routeId)

        if not routePaths.count() and not temporaryRoutePaths.count():
            if route.source.id == routeLink.start.id:
                TemporaryRoutePath.objects.create(
                    route=route,
                    routeLink=routeLink,
                    order=1,
                    createdBy=request.user,
                )
            else:
                error = "First Stop Of Route Should Be Source Of Route"
        elif temporaryRoutePaths.count():
            TemporaryRoutePath.objects.create(
                route=route,
                routeLink=routeLink,
                order=temporaryRoutePaths.last().order + 1,
                createdBy=request.user,
            )
        else:
            TemporaryRoutePath.objects.create(
                route=route,
                routeLink=routeLink,
                order=routePaths.last().order + 1,
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
        {
            "route": route,
            "routeLinks": routeLinks,
            "routePaths": routePaths,
            "error": error,
        },
    )


@login_required
def remove_route_path(request, routePathId, routeId):
    route = Route.objects.get(id=routeId)
    routeLinks = RouteLink.objects.filter(Q(verified=True) | Q(createdBy=request.user))
    routePaths = TemporaryRoutePath.objects.filter(route=routeId).order_by("order")
    error = ""

    if routePaths.count() == 1:
        if TemporaryRoutePath.objects.filter(id=routePathId).exists():
            TemporaryRoutePath.objects.filter(id=routePathId).delete()
    else:
        if TemporaryRoutePath.objects.filter(id=routePathId).exists():
            if (
                TemporaryRoutePath.objects.get(id=routePathId).routeLink.start.id
                == route.source.id
            ):
                error = "Cannot Delete First Link"
            else:
                TemporaryRoutePath.objects.filter(id=routePathId).delete()

    return render(
        request,
        "add_route_path.html",
        {
            "route": route,
            "routeLinks": routeLinks,
            "routePaths": routePaths,
            "error": error,
        },
    )


@login_required
def save_all_route_path(request, routeId):
    route = Route.objects.get(id=routeId)
    error = ""

    temporaryRoutePaths = TemporaryRoutePath.objects.filter(
        route=route, createdBy=request.user
    ).order_by("order")

    if (
        temporaryRoutePaths.count()
        and route.destination.id != temporaryRoutePaths.last().routeLink.end.id
    ):
        routeLinks = RouteLink.objects.filter(
            Q(verified=True) | Q(createdBy=request.user)
        )
        routePaths = TemporaryRoutePath.objects.filter(route=routeId).order_by("order")
        error = "Last Stop Of Route Should Be Destination Of Route"
        return render(
            request,
            "add_route_path.html",
            {
                "route": route,
                "routeLinks": routeLinks,
                "routePaths": routePaths,
                "error": error,
            },
        )

    RoutePath.objects.filter(route=route, createdBy=request.user).delete()

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
    reverseRoutePaths = routePaths.reverse()
    daHaltChoices = DaHaltTypes.choices
    error = ""
    journeyTime = {}

    if request.method == "POST":
        purpose = request.POST.get("purpose")
        daHalt = request.POST.get("da_halt")
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
                    error = f"Invalid Date selected for {routePath.routeLink.start.name} To {routePath.routeLink.end.name}"
                    break
                else:
                    journeyTime[f"start_datetime{routePath.id}"] = start_datetime
                    journeyTime[f"end_datetime{routePath.id}"] = end_datetime

            previousRoute = routePath

        if not error:
            for routePath in reverseRoutePaths:
                startDate = request.POST.get(f"revStartDate{routePath.id}")
                startTime = request.POST.get(f"revStartTime{routePath.id}")
                endDate = request.POST.get(f"revEndDate{routePath.id}")
                endTime = request.POST.get(f"revEndTime{routePath.id}")

                if startDate and startTime and endDate and endTime:
                    start_datetime = datetime.strptime(
                        f"{startDate} {startTime}", "%Y-%m-%d %H:%M"
                    )
                    end_datetime = datetime.strptime(
                        f"{endDate} {endTime}", "%Y-%m-%d %H:%M"
                    )

                    previousEndDateTime = (
                        journeyTime.get(f"end_datetime{previousRoute.id}")
                        if routePath == reverseRoutePaths[0]
                        else journeyTime.get(f"revEnd_datetime{previousRoute.id}")
                    )

                    if (previousEndDateTime > start_datetime) or (
                        start_datetime > end_datetime
                    ):
                        error = f"Invalid Date selected for {routePath.routeLink.end.name} To {routePath.routeLink.start.name}"
                        break
                    else:
                        journeyTime[f"revStart_datetime{routePath.id}"] = start_datetime
                        journeyTime[f"revEnd_datetime{routePath.id}"] = end_datetime

                previousRoute = routePath

        if not error:
            journeyRoute = JourneyRoute.objects.create(
                purpose=purpose,
                source=route.source.name,
                destination=route.destination.name,
                daHaltCondition=daHalt,
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

            for routePath in reverseRoutePaths:
                journeyRouteLink = JourneyRouteLink.objects.create(
                    start=routePath.routeLink.end.name,
                    end=routePath.routeLink.start.name,
                    mode=ModesOfTravel(routePath.routeLink.mode).label,
                    distance=routePath.routeLink.distance,
                    price=routePath.routeLink.price,
                    user=request.user,
                )
                JourneyRoutePath.objects.create(
                    route=journeyRoute,
                    routeLink=journeyRouteLink,
                    order=JourneyRoutePath.objects.filter(route=journeyRoute)
                    .order_by("order")
                    .last()
                    .order
                    + 1,
                    startDate=journeyTime.get(
                        f"revStart_datetime{routePath.id}"
                    ).date(),
                    startTime=journeyTime.get(
                        f"revStart_datetime{routePath.id}"
                    ).time(),
                    endDate=journeyTime.get(f"revEnd_datetime{routePath.id}").date(),
                    endTime=journeyTime.get(f"revEnd_datetime{routePath.id}").time(),
                    user=request.user,
                )

            return redirect("view_journeys")

    return render(
        request,
        "add_journey.html",
        {
            "route": route,
            "routePaths": routePaths,
            "reverseRoutePaths": reverseRoutePaths,
            "daHaltChoices": daHaltChoices,
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
    longestRoutePath = journeyRoutePaths.first()
    fromSource = journeyRoutePaths.first()
    fromDestination = journeyRoutePaths.last()
    journeyRoutePathsWithCalculations = []
    totalAmount = 0.0
    for journeyRoutePath in journeyRoutePaths:
        if journeyRoutePath.routeLink.distance > longestRoutePath.routeLink.distance:
            longestRoutePath = journeyRoutePath

        incidentalExpense = 0.0
        daForHalt = ""
        numberOf12Hours = (
            (
                datetime.combine(journeyRoutePath.endDate, journeyRoutePath.endTime)
                - datetime.combine(
                    journeyRoutePath.startDate, journeyRoutePath.startTime
                )
            ).total_seconds()
            / 3600
        ) / 12

        da = 600 if profile.basicPay > 70000 else 500

        if numberOf12Hours > 0.5:
            incidentalExpense = da / 2
        if numberOf12Hours > 1:
            numberOf12Hours = int(numberOf12Hours)
            incidentalExpense = +numberOf12Hours * da / 2

        print(incidentalExpense)

        if journeyRoutePaths.last() == journeyRoutePath:
            if journeyRoute.daHaltCondition == DaHaltTypes.NO_FOOD_AND_ACCOMMODATION:
                daForHalt = (numberOf12Hours / 2) * da
            elif journeyRoute.daHaltCondition == DaHaltTypes.FOOD_ONLY:
                daForHalt = (numberOf12Hours / 2) * (da / 2)
            elif journeyRoute.daHaltCondition == DaHaltTypes.ACCOMMODATION_ONLY:
                daForHalt = (numberOf12Hours / 2) * (da * (2 / 3))
            elif journeyRoute.daHaltCondition == DaHaltTypes.FOOD_AND_ACCOMMODATION:
                daForHalt = (numberOf12Hours / 2) * (da / 4)
            daForHalt = round(float(int(daForHalt)), 2)

        totalOnRow = (
            float(journeyRoutePath.routeLink.price)
            + incidentalExpense
            + (0 if not daForHalt else float(daForHalt))
        )

        totalAmount += totalOnRow

        journeyRoutePathsWithCalculations.append(
            {
                "start": journeyRoutePath.routeLink.start,
                "startDate": journeyRoutePath.startDate,
                "startTime": journeyRoutePath.startTime,
                "end": journeyRoutePath.routeLink.end,
                "endDate": journeyRoutePath.endDate,
                "endTime": journeyRoutePath.endTime,
                "distance": journeyRoutePath.routeLink.distance,
                "mode": journeyRoutePath.routeLink.mode,
                "price": journeyRoutePath.routeLink.price,
                "incidentalExpense": incidentalExpense,
                "daForHalt": daForHalt,
                "total": totalOnRow,
            }
        )

    return render(
        request,
        "generate_report.html",
        {
            "profile": profile,
            "journeyRoute": journeyRoute,
            "journeyRoutePaths": journeyRoutePathsWithCalculations,
            "total_count": len(journeyRoutePathsWithCalculations),
            "totalAmount": round(totalAmount, 2),
            "totalAmountInWords": inflect.engine().number_to_words(int(totalAmount)),
            "longestRoutePath": longestRoutePath,
            "fromSource": fromSource,
            "fromDestination": fromDestination,
        },
    )
