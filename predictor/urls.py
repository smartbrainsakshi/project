
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('predictor/', views.homepage),
    path('history/', views.history)

]