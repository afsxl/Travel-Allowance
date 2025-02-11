from django.db import models
from django.contrib.auth.models import User


class StopTypes(models.IntegerChoices):
    INTERMEDIATE_STOP = 1, "Intermediate Stop"
    INSTITUTE = 2, "Institute"
    VALUATION_CAMP = 3, "Valuation Camp"


class ModesOfTravel(models.IntegerChoices):
    TAXI = 1, "Taxi"
    TRAIN = 2, "Train"
    BUS = 3, "Bus"
    WALK = 4, "Walk"


class DaHaltTypes(models.IntegerChoices):
    NO_FOOD_AND_ACCOMMODATION = 1, "No Food And Accommodation"
    FOOD_ONLY = 2, "Food Only"
    ACCOMMODATION_ONLY = 3, "Accommodation Only"
    FOOD_AND_ACCOMMODATION = 4, "Food And Accommodation"


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    designation = models.CharField(max_length=255, null=False)
    address = models.TextField(null=False)
    basicPay = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    accountNumber = models.CharField(max_length=255, null=False)
    ifscCode = models.CharField(max_length=255, null=False)
    bankName = models.CharField(max_length=255, null=False)
    branchName = models.CharField(max_length=255, null=False)
    collegeName = models.CharField(max_length=255, null=False)
    collegeDistrict = models.CharField(max_length=255, null=False)
    address = models.TextField(null=False)


class RouteStop(models.Model):
    name = models.CharField(max_length=255, null=False)
    type = models.IntegerField(choices=StopTypes.choices, null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    verified = models.BooleanField(default=False)


class Route(models.Model):
    source = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, null=False, related_name="routeSource"
    )
    destination = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, null=False, related_name="routeDestination"
    )
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    verified = models.BooleanField(default=False)


class RouteLink(models.Model):
    start = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkStart"
    )
    end = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkEnd"
    )
    distance = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    mode = models.IntegerField(choices=ModesOfTravel.choices, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    verified = models.BooleanField(default=False)


class RoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False)
    routeLink = models.ForeignKey(RouteLink, on_delete=models.CASCADE, null=False)
    order = models.IntegerField(null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class TemporaryRoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False)
    routeLink = models.ForeignKey(RouteLink, on_delete=models.CASCADE, null=False)
    order = models.IntegerField(null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class JourneyRoute(models.Model):
    source = models.CharField(max_length=255, null=False)
    destination = models.CharField(max_length=255, null=False)
    purpose = models.CharField(max_length=255, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    daHaltCondition = models.IntegerField(choices=DaHaltTypes.choices, null=False)


class JourneyRouteLink(models.Model):
    start = models.CharField(max_length=255, null=False)
    end = models.CharField(max_length=255, null=False)
    distance = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    mode = models.CharField(max_length=255, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class JourneyRoutePath(models.Model):
    route = models.ForeignKey(JourneyRoute, on_delete=models.CASCADE, null=False)
    routeLink = models.ForeignKey(
        JourneyRouteLink, on_delete=models.CASCADE, null=False
    )
    order = models.IntegerField(null=False)
    startDate = models.DateField(null=False)
    startTime = models.TimeField(null=False)
    endDate = models.DateField(null=False)
    endTime = models.TimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
