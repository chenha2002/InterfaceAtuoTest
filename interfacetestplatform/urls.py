from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('project/', views.project, name="project"),
    path('module/',views.module,name="module"),
    path('test_case/', views.test_case, name="test_case"),
    re_path('test_case_detail/(?P<test_case_id>[0-9]+)', views.test_case_detail, name="test_case_detail"),
]