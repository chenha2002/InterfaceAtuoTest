from django.shortcuts import render, redirect
from django.contrib import auth  # Django用户认证（Auth）组件一般用在用户的登录注册上，用于判断当前的用户是否合法
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from django.contrib.auth.decorators import login_required
from .form import UserForm
import traceback
from .models import Project

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


# 登出的视图函数：重定向至login视图函数
@login_required
def logout(request):
    auth.logout(request)
    request.session.flush()
    return redirect("/login/")