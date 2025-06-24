from django.shortcuts import render, redirect,HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from django.contrib.auth.decorators import login_required

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

# Create your server here.
# 默认页的视图函数
@login_required
def index(request):
    return render(request, 'index.html')


# 注册页的视图函数
def register(request):
    return render(request, 'register.html')
















