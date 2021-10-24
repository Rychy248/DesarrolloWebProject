from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def about_us(request):
    return render(request, "us/about_us.html")

def contact_us(request):
    return render(request, "us/contact_us.html")
