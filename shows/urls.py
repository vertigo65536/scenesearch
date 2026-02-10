from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from shows import views


urlpatterns = [
    path("", views.home, name="home"),
    path("searchresults", views.searchresults, name="searchresults"),
    path("genclip/", csrf_exempt(views.get_clipdata), name="genclip"),
]
