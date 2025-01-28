from django.db import models
from django.utils.timezone import now

# Table 1: Route


class Route(models.Model):
    name = models.CharField(max_length=255, blank=False, default="Unnamed Route")
    route_id = models.AutoField(primary_key=True)
    source = models.ForeignKey('RouteStop', related_name='source_routes', on_delete=models.SET_NULL, null=True)
    destination = models.ForeignKey('RouteStop', related_name='destination_routes', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=now)
    stops = models.ManyToManyField('RouteStop', related_name='routes', blank=True)

    def save(self, *args, **kwargs):
        # Automatically set the name as "source to destination" if source and destination are provided
        if self.source and self.destination:
            self.name = f"{self.source.name} to {self.destination.name}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_at']



# Table 2: RouteStop
class RouteStop(models.Model):
    name = models.CharField(max_length=255, unique=True, default="Unnamed Stop")
    is_institute = models.BooleanField(default=False)
    is_valuationcamp = models.BooleanField(default=False)
    is_intermediate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Table 3: RouteLink
class RouteLink(models.Model):
    MODE_CHOICES = [
        ('Taxi', 'Taxi'),
        ('Train', 'Train'),
        ('Bus', 'Bus'),
        ('Walk', 'Walk'),
        ('Not Selected', 'Not Selected'),
    ]
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='links')
    start = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='link_start')
    end = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='link_end')
    distance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)  # Increased digits for distance
    mode = models.CharField(max_length=100, choices=MODE_CHOICES, default="Not Selected")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Increased digits for price

    def __str__(self):
        return f"{self.start} to {self.end} ({self.mode}, {self.distance} km, ₹{self.price})"


# Table 4: RoutePath
class RoutePath(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='paths')
    source = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='path_source')
    destination = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='path_destination')
    route_links = models.ManyToManyField(RouteLink, related_name='paths')
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Route {self.route.route_id}: {self.source} to {self.destination} (Order: {self.order})"

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['route', 'source', 'destination', 'order'], name='unique_route_path')
        ]