from django.db import models
from django.utils.timezone import now
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


class Stop(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    type = models.IntegerField(choices=StopTypes.choices, null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    verified = models.BooleanField(default=False)


class Route(models.Model):
    source = models.ForeignKey(
        Stop, on_delete=models.CASCADE, null=False, related_name="routeSource"
    )
    destination = models.ForeignKey(
        Stop, on_delete=models.CASCADE, null=False, related_name="routeDestination"
    )
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    verified = models.BooleanField(default=False)


class RouteLink(models.Model):
    start = models.ForeignKey(
        Stop, on_delete=models.CASCADE, related_name="routeLinkStart"
    )
    end = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="routeLinkEnd")
    distance = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    mode = models.IntegerField(choices=ModesOfTravel.choices, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    verified = models.BooleanField(default=False)


class RoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False)
    routeLink = models.ForeignKey(RouteLink, on_delete=models.CASCADE, null=False)
    order = models.IntegerField(null=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    verified = models.BooleanField(default=False)


class TemperoryRoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=False)
    routeLink = models.ForeignKey(RouteLink, on_delete=models.CASCADE, null=False)
    order = models.IntegerField(null=False)
