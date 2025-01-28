from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from .models import Route, RouteStop, RouteLink, RoutePath
from .forms import RouteLink,RoutePathForm, RouteForm, RouteStopForm
from django.http import JsonResponse


# User Authentication Views
def login_view(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # Clear all messages

    next_url = request.GET.get('next', 'home')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# Home View
# def home_view(request):
#     routes = Route.objects.all() 
#     return render(request, 'home.html')

def home_view(request):
    routes = Route.objects.all()
    print(Route.route_id)
    return render(request, 'home.html', {'routes': routes})




@login_required
def add_route(request):
    route_stops = RouteStop.objects.all()  # Get all route stops from the database

    if request.method == 'POST':
        source_id = request.POST.get('source')
        destination_id = request.POST.get('destination')

        if source_id and destination_id:
            source = RouteStop.objects.get(id=source_id)
            destination = RouteStop.objects.get(id=destination_id)

            # Create and save the new route with both source and destination
            route = Route.objects.create(
                source=source,
                destination=destination,
            )
            route.save()

            # Redirect to the same page with a success message
            return render(request, 'add_route.html', {'route_stops': route_stops, 'success': 'Route added successfully'})

    return render(request, 'add_route.html', {'route_stops': route_stops})




def select_route_for_link(request):
    # Fetch all routes
    routes = Route.objects.all()
    return render(request, 'select_route_for_link.html', {'routes': routes})

# def select_route_for_link(request):
#     # Fetch unique routes based on source and destination
#     routes = Route.objects.values(
#         'source', 'destination'
#     ).distinct()

#     return render(request, 'select_route_for_link.html', {'routes': routes})




@login_required
def add_route_links(request, route_id):
    route = get_object_or_404(Route, route_id=route_id)
    stops = RouteStop.objects.all() # Exclude source and destination
    last_stop = route.source  # Default to the source
    modes = RouteLink.MODE_CHOICES
    # If route links exist, set last stop as the most recent link's end
    last_link = RouteLink.objects.filter(route=route).order_by('-id').first()
    if last_link:
        last_stop = last_link.end

    if request.method == 'POST':
        start_id = request.POST.get('start')
        end_id = request.POST.get('end')
        mode = request.POST.get('mode')
        distance = request.POST.get('distance')
        price = request.POST.get('price')

        try:
            start = RouteStop.objects.get(id=start_id)
            end = RouteStop.objects.get(id=end_id)
            distance = float(distance)
            price = float(price)

            # Create a new route link
            RouteLink.objects.create(
                route=route,
                start=start,
                end=end,
                mode=mode,
                distance=distance,
                price=price,
            )
            messages.success(request, "Route link added successfully!")
            return redirect('add_route_links', route_id=route.route_id)

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, 'add_route_links.html', {
        'route': route,
        'stops': stops,
        'last_stop': last_stop,
        'modes': modes
    })

@login_required
def add_route_path(request, route_id):
    # Fetch the route using the given route_id
    route = get_object_or_404(Route, id=route_id)
    
    # Fetch source, destination, and intermediate links programmatically
    source = route.source
    destination = route.destination
    intermediate_links = RouteLink.objects.filter(route=route).order_by('id')  # Links in sequence

    # Dynamically calculate the next order for the route path
    max_order = RoutePath.objects.filter(route=route).aggregate(Max('order'))['order__max'] or 0
    next_order = max_order + 1

    try:
        # Create a new RoutePath instance
        route_path = RoutePath.objects.create(
            route=route,
            source=source,
            destination=destination,
            order=next_order,
        )

        # Associate intermediate links with the RoutePath
        route_path.route_links.set(intermediate_links)
        route_path.save()

        # Success message and redirect
        messages.success(request, "Route path added successfully!")
        return redirect('view_routes')  # Redirect to the view routes page

    except Exception as e:
        # Handle errors and display an appropriate message
        messages.error(request, f"An error occurred while saving the route path: {e}")
        return redirect('view_routes')  # Redirect to avoid breaking the flow


def view_routes(request):
    routes_with_details = []

    for route in Route.objects.all():
        # Fetch route paths, which contain source, destination, and linked route stops
        paths = RoutePath.objects.filter(route=route)
        route_data = {
            'id': route.route_id,
            'name': f"{route.source.name} to {route.destination.name}",  # Use source and destination for name
            'paths': []
        }

        for path in paths:
            route_data['paths'].append({
                'source': path.source.name,
                'destination': path.destination.name,
                'route_links': [link.start.name for link in path.route_links.all()]
            })

        routes_with_details.append(route_data)

    return render(request, 'view_routes.html', {'routes': routes_with_details})



def add_route_stop(request):
    if request.method == 'POST':
        form = RouteStopForm(request.POST)
        if form.is_valid():
            # Get the name from the form data
            route_stop_name = form.cleaned_data['name']
            
            # Check if a RouteStop with the same name already exists
            if RouteStop.objects.filter(name=route_stop_name).exists():
                messages.info(request, f"Route stop '{route_stop_name}' already exists!")
            else:
                # Save the new RouteStop if it doesn't exist
                form.save()
                messages.success(request, f"Route stop '{route_stop_name}' added successfully!")
            
            # Redirect to the same page or another page
            return redirect('add_route_stop')  # Or wherever you want the user to go after submission
    else:
        form = RouteStopForm()
    
    return render(request, 'add_route_stop.html', {'form': form})



def search_route_stops(request):
    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET.get('query', '')
        results = RouteStop.objects.filter(name__icontains=query).values('id', 'name')
        return JsonResponse(list(results), safe=False)
    return JsonResponse([], safe=False)
