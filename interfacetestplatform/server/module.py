import json

from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required

from interfacetestplatform.models import Project, Model, TestCase, CaseSuiteTestCaseExecuteRecord
from interfacetestplatform.views import get_paginator


@login_required
def module(request):
    if request.method == "GET":
        modules =Model.objects.filter().order_by('-id')
        return render(request,'module.html',{'modules':get_paginator(request, modules)})
    else:
        proj_name = request.POST['proj_name']
        projects = Project.objects.filter(name__contains=proj_name.strip())
        projs =[proj.id for proj in projects]
        modules = Model.objects.filter(belong_project__in=projs)
        return render(request,'module.html',{'modules':get_paginator(request, modules),'proj_name':proj_name.strip()})

# 模块展示测试用例
@login_required
def module_test_cases(request,module_id):
    module = ""
    if module_id:
        module = Model.objects.get(id=int(module_id))
    test_cases = TestCase.objects.filter(belong_module=module).order_by('-id')
    return render(request, 'test_case.html', {'test_cases': get_paginator(request, test_cases)})


@login_required
def suite_case_result_diff(request,suite_case_record_id):
    suite_record_data = CaseSuiteTestCaseExecuteRecord.objects.get(id=suite_case_record_id)
    present_response = suite_record_data.response_data
    if present_response:
        present_response = json.dumps(json.loads(present_response), sort_keys=True, indent=4,ensure_ascii=False)
        print("当前响应: {}".format(present_response))
    last_time_execute_response = suite_record_data.last_time_response_data
    if last_time_execute_response:
        last_time_execute_response = json.dumps(json.loads(last_time_execute_response), sort_keys=True, indent=4,ensure_ascii=False)
        print("上一次响应: {}".format(last_time_execute_response))
    return render(request,'case_suit_result_diff.html', locals())