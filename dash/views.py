from django.shortcuts import render


# Create your views here.

def dashboard(request):
    return render(request, 'dash/base_dash.html', {})
