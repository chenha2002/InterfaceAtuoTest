from django.urls import path, re_path
from . import views
from .server import login,project,module,case,suit,result


urlpatterns = [
    path('', views.index),
    path('login/', login.login),
    path('logout/', login.logout),
    path('project/', project.project, name="project"),
    path('module/',module.module,name="module"),
    path('test_case/', case.test_case, name="test_case"),
    path('edit_test_case/<int:case_id>/', case.edit_test_case,name='edit_test_case'),
    re_path('test_case_detail/(?P<test_case_id>[0-9]+)', case.test_case_detail, name="test_case_detail"),
    re_path('module_test_cases/(?P<module_id>[0-9]+)/$', module.module_test_cases, name="module_test_cases"),
    path('case_suite/',suit.test_suite,name="case_suite"),
    re_path('add_case_in_suite/(?P<suite_id>[0-9]+)', suit.add_case_in_suite, name="add_case_in_suite"),
    re_path('show_and_delete_case_in_suite/(?P<suite_id>[0-9]+)', suit.show_and_delete_case_in_suite, name="show_and_delete_case_in_suite"),
    path('test_case_execute_record/', result.test_case_execute_record, name="test_case_execute_record"),
    re_path('case_result_diff/(?P<test_record_id>[0-9]+)',result.case_result_diff, name="case_result_diff"),
    re_path('error_show/(?P<test_record_id>[0-9]+)', result.error_show, name="error_show"),


]