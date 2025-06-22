import time
import os
import traceback
import json
from . import models
from .utils.data_process import data_preprocess, assert_result, data_postprocess
from .utils.request_process import request_process


def case_task(test_case_id_list, server_address):
    global_key = 'case'+ str(int(time.time() * 100000))
    os.environ[global_key] = '{}'
    print()
    print("全局变量标识符【global_key】: {}".format(global_key))
    print("全局变量内容【os.environ[global_key]】: {}".format(os.environ[global_key]))
    for test_case_id in test_case_id_list:
        print()
        test_case = models.TestCase.objects.filter(id=int(test_case_id))[0]
        print("######### 开始执行用例【{}】 #########".format(test_case))
        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("初始请求数据: {}".format(request_data))
        print("关联参数: {}".format(extract_var))
        print("断言关键字: {}".format(assert_key))
        print("接口名称: {}".format(interface_name))
        print("所属项目: {}".format(belong_project))
        print("所属模块: {}".format(belong_module))
        print("用例维护人: {}".format(maintainer))
        print("请求方法: {}".format(request_method))
        url = "{}{}".format(server_address, interface_name)
        print("接口地址: {}".format(url))
        code, request_data, error_msg = data_preprocess(global_key, str(request_data))
        try:
            res_data = request_process(url, request_method, json.loads(request_data))
            print("响应数据: {}".format(json.dumps(res_data.json(), ensure_ascii=False)))  # ensure_ascii：兼容中文
            result_flag, exception_info = assert_result(res_data, assert_key)
            if result_flag:
                print("用例【%s】执行成功！" % test_case)
                if extract_var.strip() != "None":
                    data_postprocess(global_key, json.dumps(res_data.json(), ensure_ascii=False), extract_var)
            else:
                print("用例【%s】执行失败！" % test_case)
        except Exception as e:
            print("接口请求异常，error: {}".format(traceback.format_exc()))