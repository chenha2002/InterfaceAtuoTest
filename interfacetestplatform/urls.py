from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('project/', views.project, name="project"),
    path('module/',views.module,name="module"),
    path('test_case/', views.test_case, name="test_case"),
    path('edit_test_case/<int:case_id>/', views.edit_test_case,name='edit_test_case'),
    re_path('test_case_detail/(?P<test_case_id>[0-9]+)', views.test_case_detail, name="test_case_detail"),
    re_path('module_test_cases/(?P<module_id>[0-9]+)/$', views.module_test_cases, name="module_test_cases"),
    path('case_suite/',views.test_suite,name="case_suite"),
    re_path('add_case_in_suite/(?P<suite_id>[0-9]+)', views.add_case_in_suite, name="add_case_in_suite"),
    re_path('show_and_delete_case_in_suite/(?P<suite_id>[0-9]+)', views.show_and_delete_case_in_suite, name="show_and_delete_case_in_suite"),

]