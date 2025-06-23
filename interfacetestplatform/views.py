from django.http import HttpResponse
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import auth  # Django用户认证（Auth）组件一般用在用户的登录注册上，用于判断当前的用户是否合法
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from django.contrib.auth.decorators import login_required
from .form import UserForm
import traceback
from .models import Project, Model, TestCase,CaseSuite,SuiteCase,InterfaceServer,User
from .task import case_task

# 封装分页函数
def get_paginator(request,data):
    paginator = Paginator(data, 10)
    page = request.GET.get('page')
    try:
        paginator_pages = paginator.page(page)
    except PageNotAnInteger:
        # 如果请求的页数不是整数, 返回第一页。
        paginator_pages = paginator.page(1)
    except InvalidPage:
        # 如果请求的页数不存在, 重定向页面
        return redirect('/')
    except:
        # 其他异常
        return redirect('/')
    return paginator_pages

 # 项目管理页的视图函
@login_required
def project(request):
    print("request.user.is_authenticated: ", request.user.is_authenticated)
    projects = Project.objects.filter().order_by('-id')
    print("projects: ",projects)
    return render(request, 'project.html', {'projects': get_paginator(request, projects)})
# Create your views here.
# 默认页的视图函数
@login_required
def index(request):
    return render(request, 'index.html')


# 登录页的视图函数
def login(request):
    print("request.session.items(): {}".format(request.session.items()))

    if request.session.get('is_login', None):
        return redirect('/')
    # 如果是表单提交行为，则进行登录校验
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                # 使用django提供的身份验证功能
                user = auth.authenticate(username=username, password=password)  # 从auth_user表中匹配信息，匹配成功则返回用户对象；反之返回None
                if user is not None:
                    print("用户【%s】登录成功" % username)
                    auth.login(request, user)
                    request.session['is_login'] = True
                    # 登录成功，跳转主页
                    session_id = request.session.items()  # 打印session信息
                    print(session_id)
                    return redirect('/')

                else:
                    message = "用户名不存在或者密码不正确！"
            except:
                traceback.print_exc()
                message = "登录程序出现异常"
        # 用户名或密码为空，返回登录页和错误提示信息
        else:
            return render(request, 'login.html', locals())
    # 不是表单提交，代表只是访问登录页
    else:
        login_form = UserForm()
        return render(request, 'login.html', locals())


# 注册页的视图函数
def register(request):
    return render(request, 'register.html')
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

# 模块展示测试用例
@login_required
def module_test_cases(request,module_id):
    module = ""
    if module_id:
        module = Model.objects.get(id=int(module_id))
    test_cases = TestCase.objects.filter(belong_module=module).order_by('-id')
    return render(request, 'test_case.html', {'test_cases': get_paginator(request, test_cases)})

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









# 登出的视图函数：重定向至login视图函数
@login_required
def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect("/login/")