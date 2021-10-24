from django.urls import  path
from . import  views

urlpatterns = [
    path('',views.about_us,name="about_us"),
    path('contact_us/',views.contact_us,name="contact_us"),
]