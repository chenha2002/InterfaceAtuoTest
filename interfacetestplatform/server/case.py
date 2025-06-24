from django.contrib.auth.models import User
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import auth  # Django用户认证（Auth）组件一般用在用户的登录注册上，用于判断当前的用户是否合法
import traceback
from ..form import UserForm
from django.contrib.auth.decorators import login_required

from ..task import case_task
from ..views import get_paginator
from ..models import TestCase, InterfaceServer, Project,Model


# 获取测试用例执行的接口地址
def get_server_address(env):
    if env:  # 环境处理
        env_data = InterfaceServer.objects.filter(env=env[0])
        print("env_data: {}".format(env_data))
        if env_data:
            ip = env_data[0].ip
            port_int = env_data[0].port
            try:
                port = int(port_int)
            except (ValueError, TypeError):
                port = ''
            print("ip: {}, port: {}".format(ip, port))
            server_address = "{}".format(ip)
            if port:
                server_address += ":{}".format(port)
            print("server_address: {}".format(server_address))
            return server_address
        else:
            return ""
    else:
        return ""

# 测试用例菜单
@login_required
def test_case(request):
    print("request.session['is_login']: {}".format(request.session['is_login']))
    test_cases = ""
    if request.method == "GET":
        test_cases = TestCase.objects.filter().order_by('id')
        print("testcases: {}".format(test_cases))
    elif request.method == "POST":
        print("request.POST: {}".format(request.POST))
        test_case_id_list = request.POST.getlist('test_cases_list')
        env = request.POST.getlist('env')
        print("env: {}".format(env))
        server_address = get_server_address(env)
        if not server_address:
            return HttpResponse("提交的运行环境为空，请选择环境后再提交！")
        if test_case_id_list:
            test_case_id_list.sort()
            print("test_case_id_list: {}".format(test_case_id_list))
            print("获取到用例，开始用例执行")
            case_task(test_case_id_list, server_address)
        else:
            print("运行测试用例失败")
            return HttpResponse("提交的运行测试用例为空，请选择用例后在提交！")
        test_cases = TestCase.objects.filter().order_by('id')
    return render(request, 'test_case.html', {'test_cases': get_paginator(request, test_cases)})


# 用例修改方法
@login_required
def edit_test_case(request, case_id):
    try:
        test_case = TestCase.objects.get(id=case_id)
    except TestCase.DoesNotExist:
        return HttpResponse("测试用例不存在")

    if request.method == "GET":
        return render(request, 'edit_test_case.html', {'test_case': test_case})

    elif request.method == "POST":
        form_data = request.POST
        fields_mapping = {
            "case_name": "case_name",
            "belong_project": "belong_project",  # 这是外键字段，需要特殊处理
            "belong_module": "belong_module",  # 这是外键字段，需要特殊处理
            "request_data": "request_data",
            "uri": "uri",
            "assert_key": "assert_key",
            "maintainer": "maintainer",
            "extract_var": "extract_var",
            "request_method": "request_method",
            "user": "user"
        }

        # 处理普通字段
        for model_field, form_field in fields_mapping.items():
            if model_field not in ["belong_project", "belong_module", "user"]:
                setattr(test_case, model_field, form_data.get(form_field))

        # 特殊处理外键字段
        try:
            # 尝试根据项目名称查找Project实例
            project_name = form_data.get("belong_project")
            if project_name:
                test_case.belong_project = Project.objects.get(name=project_name)

            # 尝试根据模块名称查找Module实例
            module_name = form_data.get("belong_module")
            if module_name:
                test_case.belong_module = Model.objects.get(name=module_name)

            # 处理用户字段
            user_id = form_data.get("user")
            if user_id:
                test_case.user = User.objects.get(id=user_id)

        except (Project.DoesNotExist, Model.DoesNotExist, User.DoesNotExist) as e:
            return HttpResponse(f"关联对象不存在: {str(e)}")

        test_case.save()
        return redirect('test_case')


# 用例详情
@login_required
def test_case_detail(request,test_case_id):
    test_case_id = int(test_case_id)
    test_case = TestCase.objects.get(id=test_case_id)
    print("test_case: {}".format(test_case))
    print("test_case_id: {}".format(test_case_id))
    print("test_case.belong_project: {}".format(test_case.belong_project))
    return render(request, 'test_case_detail.html', {'test_case': test_case})