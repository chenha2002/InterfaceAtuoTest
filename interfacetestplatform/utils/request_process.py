import requests
import json
# from Util.Log import logger


# 此函数封装了get请求、post和put请求的方法
import requests
import json


def request_process(url, request_method, request_content, request_header):
    print("-------- 开始调用接口 --------")
    request_method = request_method.lower()

    # 标准化请求头的键为小写，便于统一处理
    request_header = {k.lower(): v for k, v in request_header.items()} if request_header else {}

    # 检查Content-Type是否为application/json
    is_json = 'application/json' in request_header.get('content-type', '')

    try:
        if request_method == "get":
            print("接口地址：%s" % url)
            print("请求数据：%s" % request_content)

            if isinstance(request_content, dict):
                r = requests.get(url, params=request_content, headers=request_header)
            else:
                r = requests.get(url + str(request_content), headers=request_header)

        elif request_method == "post":
            print("接口地址：%s" % url)
            print("请求数据：%s" % request_content)

            if not isinstance(request_content, dict):
                raise ValueError("请求参数不是字典类型")

            # 根据Content-Type决定使用json还是data参数
            if is_json:
                r = requests.post(url, json=request_content, headers=request_header)
            else:
                r = requests.post(url, data=request_content, headers=request_header)

        elif request_method == "put":
            print("接口地址：%s" % url)
            print("请求数据：%s" % request_content)

            if not isinstance(request_content, dict):
                raise ValueError("请求参数不是字典类型")

            # 根据Content-Type决定使用json还是data参数
            if is_json:
                r = requests.put(url, json=request_content, headers=request_header)
            else:
                r = requests.put(url, data=request_content, headers=request_header)

        else:
            raise ValueError(f"不支持的请求方法: {request_method}")

        print("响应状态码：%s" % r.status_code)
        print("响应内容：%s" % r.text)
        return r

    except ValueError as e:
        print(
            f"{request_method.upper()}方法请求发生异常：请求的url是{url}, 请求的内容是{request_content}\n发生的异常信息如下：{str(e)}")
        return None
    except Exception as e:
        print(
            f"{request_method.upper()}方法请求发生异常：请求的url是{url}, 请求的内容是{request_content}\n发生的异常信息如下：{str(e)}")
        return None