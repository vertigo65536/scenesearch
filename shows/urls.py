# cities/urls.py
from django.urls import path

from .views import HomePageView, SearchResultsView, GenClipView, ShowsAPIView
urlpatterns = [
    path("search/", SearchResultsView.as_view(), name="search_results"),
    path("", HomePageView.homepage_view, name="home"),
    path("genclip/", GenClipView.get_clipdata, name="genclip"),
    path("api/quote/", ShowsAPIView.as_view(), name="quoteapi"),
    path("api/quote/<str:query>/", ShowsAPIView.as_view()),
    path("api/quote/<str:show>/<str:query>/", ShowsAPIView.as_view())
]
