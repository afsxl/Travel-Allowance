from django.contrib import admin
from .models import  Route,RouteStop,RouteLink,RoutePath
# Register your models here.
admin.site.register(RouteStop)
admin.site.register(Route)
admin.site.register(RouteLink)
admin.site.register(RoutePath)
