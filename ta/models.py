from django.db import models
from django.utils.timezone import now


class RouteStop(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    isInstitute = models.BooleanField(default=False)
    isValuationCamp = models.BooleanField(default=False)
    isIntermediateStop = models.BooleanField(default=False)


class Route(models.Model):
    source = models.ForeignKey(
        RouteStop,
        on_delete=models.CASCADE,
        null=False,
        related_name="routeSource",
    )
    destination = models.ForeignKey(
        RouteStop,
        on_delete=models.CASCADE,
        null=False,
        related_name="routeDestination",
    )
    createdAt = models.DateTimeField(default=now)


class RouteLink(models.Model):
    MODE_CHOICES = [
        ("Taxi", "Taxi"),
        ("Train", "Train"),
        ("Bus", "Bus"),
        ("Walk", "Walk"),
        ("Not Selected", "Not Selected"),
    ]
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    start = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkStart"
    )
    end = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routeLinkEnd"
    )
    distance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="Not Selected")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class RoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    source = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routePathSource"
    )
    destination = models.ForeignKey(
        RouteStop, on_delete=models.CASCADE, related_name="routePathDestination"
    )
    order = models.PositiveIntegerField()
