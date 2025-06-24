from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required

from interfacetestplatform.models import Project, Model, TestCase
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