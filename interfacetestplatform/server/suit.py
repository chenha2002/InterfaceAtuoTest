from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from ..views import get_paginator
from ..models import CaseSuite, TestCase, SuiteCase


# 用例集合展示
@login_required
def test_suite(request):
    case_suites = CaseSuite.objects.filter().order_by('-create_time')
    return render(request,'case_suite.html',{'case_suites': get_paginator(request, case_suites)})

# 用例集合—添加测试用例页
@login_required
def add_case_in_suite(request,suite_id):
    # 查询指定的用例集合
    case_suite = CaseSuite.objects.get(id = suite_id)
    # 根据id查所有的用例
    test_cases = TestCase.objects.filter().order_by('id')
    if request.method == "GET":
        print("test cases",test_cases)
    elif request.method == "POST":
        test_cases_list = request.POST.getlist('testcases_list')
        # 如果页面勾选了用例
        if test_cases_list:
            print("勾选用例id",test_cases_list)
            # 根据页面勾选的用例与查询出来的所有用例一一比较
            for test_case in test_cases_list:
                test_case = TestCase.objects.get(id=int(test_case))
                # 匹配成功则添加用例
                SuiteCase.objects.create(case_suite=case_suite,test_case=test_case)
        # 未勾选用例
        else:
            print("添加测试用例失败")
            return HttpResponse("添加的测试用例为空，请选择用例后再添加！")
    return render(request,'add_case_in_suite.html',{'test_cases': get_paginator(request, test_cases),'case_suite':case_suite})

# 用例集合—查看/删除
@login_required
def show_and_delete_case_in_suite(request,suite_id):
    case_suite = CaseSuite.objects.get(id = int(suite_id))
    test_cases = SuiteCase.objects.filter(case_suite=case_suite)
    if request.method == "POST":
        test_cases_list = request.POST.getlist("test_cases_list")
        if test_cases_list:
            print("勾选用例",test_cases_list)
            for test_case in test_cases_list:
                test_case = TestCase.objects.get(id=int(test_case))
                SuiteCase.objects.filter(case_suite=case_suite,test_case=test_case).delete()
        else:
            print("测试用例删除失败")
            return HttpResponse("所选测试用例为空，请选择用例后再进行删除！")
    case_suite = CaseSuite.objects.get(id=int(suite_id))
    return render(request,'show_and_delete_case_in_suite.html',{'test_cases': get_paginator(request, test_cases),'case_suite':case_suite})