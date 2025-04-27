from django.http import HttpResponse
from django.shortcuts import render

def to_text(request):
    return render(request, 'to_text.html')
