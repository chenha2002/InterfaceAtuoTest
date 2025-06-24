from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from ..views import get_paginator
from ..models import Project


# 项目管理页的视图函
@login_required
def project(request):
    print("request.user.is_authenticated: ", request.user.is_authenticated)
    projects = Project.objects.filter().order_by('-id')
    print("projects: ",projects)
    return render(request, 'project.html', {'projects': get_paginator(request, projects)})