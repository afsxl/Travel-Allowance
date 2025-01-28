from django import forms
from .models import Route, RouteStop, RouteLink, RoutePath


# Form for Route
class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['source', 'destination', 'stops'] # Updated fields to match the model
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter route name'}),
            'stops': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Route Name',
            'stops': 'Stops',
        }


# Form for RouteStop
class RouteStopForm(forms.ModelForm):
    class Meta:
        model = RouteStop
        fields = ['name', 'is_institute', 'is_valuationcamp', 'is_intermediate']

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stop name'}),
        label='Stop Name'
    )
    is_institute = forms.BooleanField(required=False, label="Is Institute")
    is_valuationcamp = forms.BooleanField(required=False, label="Is Valuation Camp")
    is_intermediate = forms.BooleanField(required=False, label="Is Intermediate Stop")


# Form for RouteLink
class RouteLinkForm(forms.ModelForm):
    class Meta:
        model = RouteLink
        fields = ['start', 'end', 'distance', 'mode', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start'].queryset = RouteStop.objects.all()
        self.fields['end'].queryset = RouteStop.objects.all()

        self.fields['distance'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter distance in km',
            'step': '0.01',
        })
        self.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter price in ₹',
            'step': '0.01',
        })

        self.fields['mode'].choices = [('', 'Select Mode')] + list(RouteLink.CHOICES)


# Form for RoutePath
class RoutePathForm(forms.ModelForm):
    class Meta:
        model = RoutePath
        fields = ['route', 'route_links', 'source', 'destination', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].queryset = Route.objects.all()
        self.fields['route_links'].queryset = RouteLink.objects.all()
        self.fields['source'].queryset = RouteStop.objects.all()
        self.fields['destination'].queryset = RouteStop.objects.all()

        self.fields['order'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter the order number',
        })
