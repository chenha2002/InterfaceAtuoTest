import re
import hashlib
import os
import json
import traceback
import redis
from InterfaceAutoTest.settings import redis_port


"""
断言格式支持：
示例1：JSON格式关键字匹配
assert_result(response_obj, '"status_code":200')  # 匹配成功

示例2：嵌套JSON格式匹配
assert_result(response_obj, '{"body.0.category.name":"Dogs", "status":"available"}')

示例3：混合格式匹配
assert_result(response_obj, '"status_code":200 && body.id=12345')

示例4：数组包含匹配
assert_result(response_obj, '{"body":[{"status":"available"}]}')

"""

# 连接redis
pool = redis.ConnectionPool(host='localhost', port=redis_port, decode_responses=True)
redis_obj = redis.Redis(connection_pool=pool)


# 初始化框架工程中的全局变量，存储在测试数据中的唯一值数据
# 框架工程中若要使用字典中的任意一个变量，则每次使用后，均需要将字典中的value值进行加1操作。
def get_unique_number_value(unique_number):
    data = None
    try:
        redis_value = redis_obj.get(unique_number)  # {"unique_number": 666}
        if redis_value:
            data = redis_value
            print("全局唯一数当前生成的值是：%s" % data)
            # 把redis中key为unique_number的值进行加一操作，以便下提取时保持唯一
            redis_obj.set(unique_number, int(redis_value) + 1)
        else:
            data = 1000  # 初始化递增数值
            redis_obj.set(unique_number, data)
    except Exception as e:
        print("获取全局唯一数变量值失败，请求的全局唯一数变量是%s,异常原因如下：%s" % (unique_number, traceback.format_exc()))
        data = None
    finally:
        return data


def md5(s):
    m5 = hashlib.md5()
    m5.update(s.encode("utf-8"))
    md5_value = m5.hexdigest()
    return md5_value


# 请求数据预处理：参数化、函数化
# 将请求数据中包含的${变量名}的字符串部分，替换为唯一数或者全局变量字典中对应的全局变量
def data_preprocess(global_key, requestData):
    try:
        # 匹配注册用户名参数，即"${unique_num...}"的格式，并取出本次请求的随机数供后续接口的用户名参数使用
        if re.search(r"\$\{unique_num\d+\}", requestData):
            var_name = re.search(r"\$\{(unique_num\d+)\}", requestData).group(1)  # 获取用户名参数
            print("用户名变量:%s" % var_name)
            var_value = get_unique_number_value(var_name)
            print("用户名变量值: %s" % var_value)
            requestData = re.sub(r"\$\{unique_num\d+\}", str(var_value), requestData)
            var_name = var_name.split("_")[1]
            print("关联的用户名变量: %s" % var_name)
            # "xxxkey" : "{'var_name': var_value}"
            global_var = json.loads(os.environ[global_key])
            global_var[var_name] = var_value
            os.environ[global_key] = json.dumps(global_var)
            print("用户名唯一数参数化后的全局变量【os.environ[global_key]】: {}".format(os.environ[global_key]))
        # 函数化，如密码加密"${md5(...)}"的格式
        if re.search(r"\$\{\w+\(.+\)\}", requestData):
            var_pass = re.search(r"\$\{(\w+\(.+\))\}", requestData).group(1)  # 获取密码参数
            print("需要函数化的变量: %s" % var_pass)
            print("函数化后的结果: %s" % eval(var_pass))
            requestData = re.sub(r"\$\{\w+\(.+\)\}", eval(var_pass), requestData)  # 将requestBody里面的参数内容通过eval修改为实际变量值
            print("函数化后的请求数据: %s" % requestData)  # requestBody是拿到的请求时发送的数据
        # 其余变量参数化
        if re.search(r"\$\{(\w+)\}", requestData):
            print("需要参数化的变量: %s" % (re.findall(r"\$\{(\w+)\}", requestData)))
            for var_name in re.findall(r"\$\{(\w+)\}", requestData):
                requestData = re.sub(r"\$\{%s\}" % var_name, str(json.loads(os.environ[global_key])[var_name]), requestData)
        print("变量参数化后的最终请求数据: %s" % requestData)
        print("数据参数后的最终全局变量【os.environ[global_key]】: {}".format(os.environ[global_key]))
        return 0, requestData, ""
    except Exception as e:
        print("请求数据预处理发生异常，error：{}".format(traceback.format_exc()))
        return 1, {}, traceback.format_exc()


# 响应数据提取关联参数
def data_postprocess(global_key, response_data, extract_var):
    print("需提取的关联变量：%s" % extract_var)
    var_name = extract_var.split("||")[0]
    print("关联变量名：%s" % var_name)
    regx_exp = extract_var.split("||")[1]
    print("关联变量正则：%s" % regx_exp)
    if re.search(regx_exp, response_data):
        global_vars = json.loads(os.environ[global_key])
        print("关联前的全局变量：{}".format(global_vars))
        global_vars[var_name] = re.search(regx_exp, response_data).group(1)
        os.environ[global_key] = json.dumps(global_vars)
        print("关联前的全局变量：{}".format(os.environ[global_key]))
    return


import json
import traceback
from typing import Tuple, Dict, Any, List

import json
import traceback
from typing import Tuple, Dict, Any, List


def assert_result(response_obj, key_word: str) -> Tuple[bool, str]:
    """
    增强版接口响应断言函数，支持JSON格式关键字匹配
    """
    try:
        # 构建响应信息字典
        response_info = {
            'status_code': response_obj.status_code,
            'headers': dict(response_obj.headers),
            'body': response_obj.json()
        }

        print("响应数据：")
        print(json.dumps(response_info, ensure_ascii=False, indent=2))

        # 处理多关键字断言
        if '&&' in key_word:
            key_word_list = [kw.strip() for kw in key_word.split('&&') if kw.strip()]
            print(f"断言关键字列表：{key_word_list}")

            flag = True
            exception_info = ""
            response_json = json.dumps(response_info, ensure_ascii=False)

            for kw in key_word_list:
                if not kw:
                    continue

                # 优先尝试解析为JSON格式断言
                match_result = _parse_json_assert(kw, response_info)
                if match_result[0]:
                    print(f"断言关键字【{kw}】匹配成功")
                else:
                    # 解析失败则回退到旧逻辑
                    match_result = _safe_match(kw, response_info)
                    if match_result[0]:
                        print(f"断言关键字【{kw}】匹配成功")
                    else:
                        print(f"断言关键字【{kw}】匹配失败")
                        flag = False
                        exception_info = f"keyword: {kw} not matched"

            return flag, exception_info

        # 处理单个关键字断言
        else:
            if not key_word:
                return True, ""

            # 优先尝试JSON格式解析
            match_result = _parse_json_assert(key_word, response_info)
            if match_result[0]:
                print(f"接口断言【{key_word}】匹配成功！")
                return True, ""

            # 回退到旧逻辑
            match_result = _safe_match(key_word, response_info)
            if match_result[0]:
                print(f"接口断言【{key_word}】匹配成功！")
                return True, ""
            else:
                print(f"接口断言【{key_word}】匹配失败！")
                return False, f"keyword: {key_word} not matched"

    except Exception as e:
        error_msg = f"断言异常: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return False, error_msg


def _parse_json_assert(assert_str: str, response_data: Dict[str, Any]) -> Tuple[bool, str]:
    """解析JSON格式的断言字符串（如"status_code":200）"""
    try:
        # 尝试将断言字符串解析为JSON对象
        # 处理单引号和转义问题，确保JSON合法
        json_assert = assert_str.replace("'", '"')
        if not (json_assert.startswith('{') and json_assert.endswith('}')):
            json_assert = '{' + json_assert + '}'

        # 解析JSON断言
        assert_obj = json.loads(json_assert)

        # 深度匹配响应数据
        return _deep_match(response_data, assert_obj), ""

    except json.JSONDecodeError:
        return False, f"无效的JSON断言格式: {assert_str}"
    except Exception as e:
        return False, f"解析断言失败: {str(e)}"


def _deep_match(response_data: Any, assert_obj: Any) -> bool:
    """深度匹配响应数据与断言对象"""
    # 处理字典类型断言
    if isinstance(assert_obj, dict):
        if not isinstance(response_data, dict):
            return False
        for key, value in assert_obj.items():
            if key not in response_data:
                return False
            if not _deep_match(response_data[key], value):
                return False
        return True

    # 处理列表类型断言（检查包含关系）
    if isinstance(assert_obj, list):
        if not isinstance(response_data, list):
            return False
        for item in assert_obj:
            if not any(_deep_match(elem, item) for elem in response_data):
                return False
        return True

    # 处理基础类型断言（支持类型自动转换）
    return _type_safe_equal(response_data, assert_obj)


def _type_safe_equal(val1: Any, val2: Any) -> bool:
    """类型安全的相等性判断"""
    # 尝试转换为相同类型比较
    try:
        # 数值类型比较
        if isinstance(val1, (int, float)) and isinstance(val2, str) and val2.isdigit():
            return val1 == int(val2)
        if isinstance(val2, (int, float)) and isinstance(val1, str) and val1.isdigit():
            return int(val1) == val2

        # 布尔类型比较
        if isinstance(val1, bool) and isinstance(val2, str) and val2.lower() in ['true', 'false']:
            return val1 == (val2.lower() == 'true')
        if isinstance(val2, bool) and isinstance(val1, str) and val1.lower() in ['true', 'false']:
            return (val1.lower() == 'true') == val2

        # 字符串类型比较（忽略前后空格）
        if isinstance(val1, str) and isinstance(val2, str):
            return val1.strip() == val2.strip()

        # 基础类型直接比较
        return val1 == val2

    except Exception:
        return False


def _safe_match(keyword: str, response_data: Dict[str, Any]) -> Tuple[bool, str]:
    """旧版安全匹配逻辑（保留兼容）"""
    # 处理数值类型
    if keyword.isdigit():
        return _deep_search(response_data, int(keyword), type_check=True)

    # 处理布尔类型
    if keyword.lower() in ['true', 'false']:
        return _deep_search(response_data, keyword.lower() == 'true', type_check=True)

    # 处理key=value格式
    if '=' in keyword:
        path, expected = keyword.split('=', 1)
        path = path.strip()
        expected = expected.strip()
        if expected.isdigit():
            expected = int(expected)
        elif expected.lower() in ['true', 'false']:
            expected = expected.lower() == 'true'
        return _deep_search(response_data, expected, path=path, type_check=True)

    # 字符串包含匹配
    response_json = json.dumps(response_data, ensure_ascii=False)
    return keyword in response_json, ""


def _deep_search(data: Any, target: Any, path: str = None, type_check: bool = False) -> Tuple[bool, str]:
    """深度搜索数据结构（保留兼容）"""
    if path:
        keys = path.split('.')
        current = data
        for key in keys:
            if key.isdigit() and isinstance(current, list):
                index = int(key)
                if index >= len(current):
                    return False, f"路径 {path} 不存在"
                current = current[index]
            elif isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False, f"路径 {path} 不存在"
        if type_check:
            return current == target, ""
        return str(current) == str(target), ""

    if isinstance(data, dict):
        for k, v in data.items():
            match, msg = _deep_search(v, target, type_check=type_check)
            if match:
                return True, ""
    elif isinstance(data, list):
        for item in data:
            match, msg = _deep_search(item, target, type_check=type_check)
            if match:
                return True, ""
    if type_check:
        return data == target, ""
    return str(data) == str(target), ""


# 测试代码
if __name__ == "__main__":
    print(get_unique_number_value("unique_num1"))