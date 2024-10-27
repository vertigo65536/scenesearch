# cities/urls.py
from django.urls import path

from .views import HomePageView, SearchResultsView, GenClipView

urlpatterns = [
    path("search/", SearchResultsView.as_view(), name="search_results"),
    path("", HomePageView.as_view(), name="home"),
    path("genclip/", GenClipView.get_clipdata, name="genclip"),
]
