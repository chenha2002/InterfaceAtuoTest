import re
import hashlib
import os
import redis
from InterfaceAutoTest.settings import redis_port
import json
import traceback
from typing import Tuple, Dict, Any, List


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



提取格式支持
变量名||正则表达式
extract_var = "token||<token>(.*?)</token>"

变量名$$JSON路径
extract_var = "userId$$user.id"  # 从 {"user": {"id": 123}} 中提取123
extract_var = "firstItem$$items[0].name"  # 从数组中提取第一个元素的name字段
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
import re
import json
import os
import traceback


def data_preprocess(global_key, request_data, request_headers):
    """
    预处理请求数据和请求头，支持参数化和函数化处理

    Args:
        global_key: 全局变量在环境变量中的键名
        request_data: 请求体数据（字符串或字典）
        request_headers: 请求头数据（字典）

    Returns:
        (error_code, processed_data, error_message, processed_headers)
    """
    try:
        # 初始化请求头处理结果
        processed_headers = request_headers if request_headers else {}

        # ===== 处理请求体数据 =====
        # 转换为字符串以便正则匹配（如果是字典则转为JSON字符串）
        if isinstance(request_data, dict):
            data_str = json.dumps(request_data)
        else:
            data_str = str(request_data)

        # 匹配注册用户名参数
        if re.search(r"\$\{unique_num\d+\}", data_str):
            var_name = re.search(r"\$\{(unique_num\d+)\}", data_str).group(1)
            print("用户名变量:%s" % var_name)
            var_value = get_unique_number_value(var_name)
            print("用户名变量值: %s" % var_value)
            data_str = re.sub(r"\$\{unique_num\d+\}", str(var_value), data_str)
            var_name = var_name.split("_")[1]
            print("关联的用户名变量: %s" % var_name)
            global_var = json.loads(os.environ[global_key])
            global_var[var_name] = var_value
            os.environ[global_key] = json.dumps(global_var)
            print("用户名唯一数参数化后的全局变量【os.environ[global_key]】: {}".format(os.environ[global_key]))

        # 处理函数化参数（如密码加密）
        if re.search(r"\$\{\w+\(.+\)\}", data_str):
            var_pass = re.search(r"\$\{(\w+\(.+\))\}", data_str).group(1)
            print("需要函数化的变量: %s" % var_pass)
            func_result = eval(var_pass)
            print("函数化后的结果: %s" % func_result)
            data_str = re.sub(r"\$\{\w+\(.+\)\}", str(func_result), data_str)
            print("函数化后的请求数据: %s" % data_str)

        # 处理其余变量参数化
        if re.search(r"\$\{(\w+)\}", data_str):
            var_names = re.findall(r"\$\{(\w+)\}", data_str)
            print("需要参数化的变量: %s" % var_names)
            global_var = json.loads(os.environ[global_key])
            for var_name in var_names:
                if var_name in global_var:
                    data_str = re.sub(r"\$\{%s\}" % var_name, str(global_var[var_name]), data_str)
                else:
                    print(f"警告：全局变量中未找到 {var_name}")

        print("变量参数化后的最终请求数据: %s" % data_str)
        print("数据参数后的最终全局变量【os.environ[global_key]】: {}".format(os.environ[global_key]))

        # 转换回原始类型（如果是字典则解析为字典）
        if isinstance(request_data, dict):
            processed_data = json.loads(data_str)
        else:
            processed_data = data_str

        # ===== 处理请求头数据 =====
        if processed_headers:
            print("开始处理请求头参数化...")
            # 确保processed_headers是字典类型
            if isinstance(processed_headers, str):
                try:
                    processed_headers = json.loads(processed_headers)
                except json.JSONDecodeError:
                    print(f"错误：无法将请求头解析为字典。原始值：{processed_headers}")
                    processed_headers = {}  # 解析失败时置为空字典

            for header_name, header_value in processed_headers.items():
                if not isinstance(header_value, str):
                    header_value = str(header_value)

                # 处理用户名参数
                if re.search(r"\$\{unique_num\d+\}", header_value):
                    var_name = re.search(r"\$\{(unique_num\d+)\}", header_value).group(1)
                    print(f"请求头中发现用户名变量: {var_name}")
                    var_value = get_unique_number_value(var_name)
                    header_value = re.sub(r"\$\{unique_num\d+\}", str(var_value), header_value)
                    var_name = var_name.split("_")[1]
                    global_var = json.loads(os.environ[global_key])
                    global_var[var_name] = var_value
                    os.environ[global_key] = json.dumps(global_var)
                    print(f"请求头用户名参数化后: {header_value}")

                # 处理函数化参数
                if re.search(r"\$\{\w+\(.+\)\}", header_value):
                    var_func = re.search(r"\$\{(\w+\(.+\))\}", header_value).group(1)
                    print(f"请求头中需要函数化的变量: {var_func}")
                    func_result = eval(var_func)
                    header_value = re.sub(r"\$\{\w+\(.+\)\}", str(func_result), header_value)
                    print(f"请求头函数化后的结果: {header_value}")

                # 处理其余变量参数化
                if re.search(r"\$\{(\w+)\}", header_value):
                    var_names = re.findall(r"\$\{(\w+)\}", header_value)
                    print(f"请求头中需要参数化的变量: {var_names}")
                    global_var = json.loads(os.environ[global_key])
                    for var_name in var_names:
                        if var_name in global_var:
                            header_value = re.sub(r"\$\{%s\}" % var_name, str(global_var[var_name]), header_value)
                        else:
                            print(f"警告：请求头变量 {var_name} 未在全局变量中找到")

                # 更新处理后的请求头值
                processed_headers[header_name] = header_value

            print("请求头参数化后的结果: %s" % processed_headers)

        return 0, processed_data, "", processed_headers  # 修改返回值顺序

    except Exception as e:
        print("请求数据预处理发生异常，error：{}".format(traceback.format_exc()))
        return 1, {}, traceback.format_exc(), {}  # 修改返回值顺序


# 响应数据提取关联参数
def data_postprocess(global_key, response_data, extract_var):
    try:
        # 确保全局变量环境变量存在
        if global_key not in os.environ:
            os.environ[global_key] = json.dumps({})

        print(f"需提取的关联变量：{extract_var}")

        # 判断提取方式
        if "$$" in extract_var:  # JSON提取方式
            var_name, json_path = extract_var.split("$$", 1)
            print(f"关联变量名：{var_name}")
            print(f"JSON路径：{json_path}")

            # 尝试解析响应数据为JSON
            try:
                json_data = json.loads(response_data)
            except json.JSONDecodeError:
                print(f"警告: 响应数据不是有效的JSON格式，无法使用JSON提取")
                return f"{var_name}：提取失败（非JSON响应）"

            # 使用JSONPath提取值
            value = extract_json_value(json_data, json_path)
            if value is not None:
                # 将提取的变量保存到全局变量
                save_to_global_vars(global_key, var_name, value)
                print(f"成功从JSON中提取变量 {var_name} = {value}")
                return f"{var_name}：{value}"
            else:
                print(f"警告: JSON路径 {json_path} 在响应中未找到匹配值")
                return f"{var_name}：未找到匹配值"

        elif "||" in extract_var:  # 正则表达式方式（原有逻辑）
            var_name, regx_exp = extract_var.split("||", 1)
            print(f"关联变量名：{var_name}")
            print(f"关联变量正则：{regx_exp}")

            if re.search(regx_exp, response_data):
                var_value = re.search(regx_exp, response_data).group(1)
                # 将提取的变量保存到全局变量
                save_to_global_vars(global_key, var_name, var_value)
                print(f"成功从正则表达式提取变量 {var_name} = {var_value}")
                return f"{var_name}：{var_value}"
            else:
                print(f"警告: 正则表达式 {regx_exp} 在响应中未匹配到任何内容")
                return f"{var_name}：未找到匹配值"

        else:
            raise ValueError(f"提取变量格式错误: {extract_var}，应使用'变量名||正则表达式'或'变量名$$json路径'格式")

    except Exception as e:
        print(f"提取变量时发生异常: {str(e)}")
        return f"提取失败: {str(e)}"


# 辅助函数：根据JSONPath提取值
def extract_json_value(data, path):
    """
    根据JSONPath提取JSON中的值

    支持的路径格式示例:
    - root-level: "key"
    - nested: "key1.key2"
    - array: "key1[0].key2"
    """
    try:
        parts = path.split('.')
        current = data

        for part in parts:
            # 处理数组索引
            if '[' in part and ']' in part:
                key, index = part.split('[')
                index = int(index.replace(']', ''))
                if key:
                    current = current[key]
                current = current[index]
            else:
                current = current[part]

        return current
    except (KeyError, IndexError, TypeError) as e:
        print(f"JSONPath解析错误: {path}, 错误: {str(e)}")
        return None


# 辅助函数：安全地将变量保存到全局环境变量
def save_to_global_vars(global_key, var_name, value):
    """将变量安全地保存到全局环境变量"""
    try:
        # 从环境变量加载当前全局变量
        global_vars = json.loads(os.environ.get(global_key, '{}'))

        # 保存新变量
        global_vars[var_name] = value

        # 更新环境变量
        os.environ[global_key] = json.dumps(global_vars)

        print(f"已将变量保存到全局环境: {var_name} = {value}")
    except Exception as e:
        print(f"保存全局变量失败: {str(e)}")




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