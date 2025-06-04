from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('project/', views.project, name="project"),
    path('module/',views.module,name="module"),
]