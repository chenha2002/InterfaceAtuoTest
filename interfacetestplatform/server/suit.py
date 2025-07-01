from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required

from .case import get_server_address
from ..task import suite_task
from ..views import get_paginator
from ..models import CaseSuite, TestCase, SuiteCase, CaseSuiteExecuteRecord


# 用例集合展示
@login_required
def case_suite(request):
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

# 用例集合菜单选项
@login_required
def case_suite(request):
    if request.method == "POST":
        count_down_time = 0
        if request.POST['delay_time']:
            print("输入的延迟时间是: {}".format(request.POST['delay_time']))
            try:
                count_down_time = int(request.POST['delay_time'])
            except:
                print("输入的延迟时间是非数字！")
        else:
            print("没有输入延迟时间")
        env = request.POST.getlist('env')
        print("env: {}".format(env))
        server_address = get_server_address(env)
        if not server_address:
            return HttpResponse("提交的运行环境为空，请选择环境后再提交！")
        case_suite_list = request.POST.getlist('case_suite_list')
        if case_suite_list:
            print("所需执行的用例集合列表：", case_suite_list)
            for suite_id in case_suite_list:
                test_suite = CaseSuite.objects.get(id=int(suite_id))
                print("所需执行的用例集合: {}".format(test_suite))
                username = request.user.username
                test_suite_record = CaseSuiteExecuteRecord.objects.create(case_suite=test_suite,
                                                                               run_time=count_down_time,
                                                                               creator=username)
                suite_task(test_suite_record, test_suite, server_address)
        else:
            print("运行测试集合用例失败")
            return HttpResponse("运行的测试集合为空，请选择测试集合后再运行！")
    case_suites = CaseSuite.objects.filter()
    return render(request, 'case_suite.html', {'case_suites': get_paginator(request, case_suites)})

