import json

from django.http import JsonResponse
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from ..views import get_paginator
from ..models import Project, TestCaseExecuteResult,CaseSuiteTestCaseExecuteRecord,CaseSuiteExecuteRecord


# 测试结果的展示
@login_required
def test_case_execute_record(request):
    test_case_execute_records = TestCaseExecuteResult.objects.filter().order_by('-id')
    return render(request, 'test_case_execute_records.html',
                {'test_case_execute_records': get_paginator(request, test_case_execute_records)})

# 用例执行结果—对比差异
@login_required
def case_result_diff(request,test_record_id):
    test_record_data = TestCaseExecuteResult.objects.get(id=test_record_id)
    print("用例执行结果记录: {}".format(test_record_data))
    present_response = test_record_data.response_data
    if present_response:
        present_response = json.dumps(json.loads(present_response), sort_keys=True, indent=4,
                                      ensure_ascii=False)  # 中文字符不转ascii编码
        print("当前响应结果: {}".format(present_response))
    last_time_execute_response = test_record_data.last_time_response_data
    if last_time_execute_response:
        last_time_execute_response = json.dumps(json.loads(last_time_execute_response), sort_keys=True, indent=4,
                                                ensure_ascii=False)
    print("上一次响应结果: {}".format(last_time_execute_response))
    return render(request, 'case_result_diff.html', locals())

# 用例执行结果—显示异常信息
@login_required
def error_show(request,test_record_id):
    test_record_data = TestCaseExecuteResult.objects.get(id=test_record_id)
    print("用例执行结果记录: {}".format(test_record_data))
    errors = test_record_data.exception_info
    return render(request,'error_show.html',{'errors': errors})

# @login_required
# @csrf_protect

# def delete_case_result_diff(request, test_record_id):
#     if request.method == 'POST':
#         test_record_data = TestCaseExecuteResult.objects.get(id=test_record_id)
#         test_record_data.delete()
#         return JsonResponse({'status': 'success'})
#     return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# 用例执行结果—菜单项
@login_required
def case_suite_execute_record(request):
    case_suite_execute_records = CaseSuiteExecuteRecord.objects.select_related(
        'case_suite'
    ).order_by('-id')
    return render(request,'case_suite_execute_record.html',{'case_suite_execute_records': get_paginator(request, case_suite_execute_records)})

# 用例集合执行结果——用例结果展示
@login_required
def suite_case_execute_record(request,suite_record_id):
    case_suite_execute_record = CaseSuiteExecuteRecord.objects.get(id=suite_record_id)
    suite_case_execute_records =CaseSuiteTestCaseExecuteRecord.objects.filter(case_suite_record=case_suite_execute_record)
    return render(request,'suite_case_execute_record.html',{'suite_case_execute_records': get_paginator(request,suite_case_execute_records)})

# 用例集合执行结果—包含用例结果展示—差异对比


# 用例集合执行结果——包含用例结果展示——异常信息展示
@login_required
def suite_case_exception(request, suite_case_record_id):
    test_record_data = CaseSuiteTestCaseExecuteRecord.objects.get(id=suite_case_record_id)
    errors = test_record_data.exception_info
    return render(request,'error_show.html',{'errors': errors})
