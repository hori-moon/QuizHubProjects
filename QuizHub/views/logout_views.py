from django.contrib.auth import logout
from django.shortcuts import render

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')
