from django.db import models
from django.utils.timezone import now


class StopTypes(models.IntegerChoices):
    INTERMEDIATE_STOP = 1, "Intermediate Stop"
    INSTITUTE = 2, "Institute"
    VALUATION_CAMP = 3, "Valuation Camp"


class ModesOfTravel(models.IntegerChoices):
    TAXI = 1, "Taxi"
    TRAIN = 2, "Train"
    BUS = 3, "Bus"
    WALK = 4, "Walk"


class RouteStop(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    stopType = models.IntegerField(choices=StopTypes.choices, null=False)


class Route(models.Model):
    source = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, null=False, related_name="routeSource"
    )
    destination = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, null=False, related_name="routeDestination"
    )
    createdAt = models.DateTimeField(default=now)


class TemporaryRouteLink(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    start = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="temporaryRouteLinkStart"
    )
    end = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="temporaryRouteLinkEnd"
    )
    distance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mode = models.IntegerField(choices=ModesOfTravel.choices, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order = models.IntegerField(null=False)


class RouteLink(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    start = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkStart"
    )
    end = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkEnd"
    )
    distance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mode = models.IntegerField(choices=ModesOfTravel.choices, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order = models.IntegerField(null=False)
