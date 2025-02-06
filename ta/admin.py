from django.contrib import admin
from .models import *

admin.site.register(Stop)
admin.site.register(Route)
admin.site.register(RouteLink)
admin.site.register(RoutePath)
admin.site.register(TemperoryRoutePath)
