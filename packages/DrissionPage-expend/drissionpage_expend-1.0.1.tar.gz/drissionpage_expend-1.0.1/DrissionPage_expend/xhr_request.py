"""
DrissionPage XHR请求封装模块
使用chromium实例的run_js方法执行JavaScript XHR请求
"""

import json
from typing import Dict, Any, Optional, Union


class XHRResponse:
    """封装XHR响应的类"""

    def __init__(self, status_code: int, response_text: str, headers: Dict[str, str], url: str):
        self.status_code = status_code
        self.text = response_text
        self.headers = headers
        self.url = url
        self._json_data = None

    @property
    def json(self) -> Dict[str, Any]:
        """解析响应为JSON"""
        if self._json_data is None:
            try:
                self._json_data = json.loads(self.text)
            except json.JSONDecodeError:
                raise ValueError("响应内容不是有效的JSON格式")
        return self._json_data

    @property
    def ok(self) -> bool:
        """检查请求是否成功"""
        return 200 <= self.status_code < 300

    def __repr__(self):
        return f"<XHRResponse [{self.status_code}]>"


class XHRClient:
    """XHR请求客户端类"""

    def __init__(self, chromium_instance):
        """
        初始化XHR客户端

        Args:
            chromium_instance: DrissionPage的chromium实例
        """
        self.chromium = chromium_instance


    def request(self, method: str, url: str,
                data: Optional[Union[Dict[str, Any], str, bytes]] = None,
                json_data: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行XHR请求

        Args:
            method: HTTP方法 ('GET', 'POST', 'PUT', 'DELETE' 等)
            url: 请求的URL
            data: 请求数据，可以是:
                  - Dict: 将作为表单数据发送 (application/x-www-form-urlencoded)
                  - str: 将作为原始文本发送
                  - bytes: 将作为二进制数据发送
            json_data: JSON数据字典，如果提供则会覆盖data参数
            headers: 自定义请求头字典

        Returns:
            XHRResponse: 封装的响应对象

        Raises:
            Exception: 当请求失败时抛出异常

        Note:
            使用同步XHR请求，不支持timeout设置
        """

        # 准备请求数据
        method = method.upper()
        headers = headers or {}

        # 确定发送的数据和Content-Type
        send_data = None
        content_type = None

        if json_data is not None:
            # JSON数据优先级最高
            send_data = json.dumps(json_data, ensure_ascii=False)
            content_type = 'application/json; charset=utf-8'
        elif data is not None:
            if isinstance(data, dict):
                # 字典数据作为表单发送
                params = []
                for key, value in data.items():
                    params.append(f"{key}={value}")
                send_data = "&".join(params)
                content_type = 'application/x-www-form-urlencoded; charset=utf-8'
            elif isinstance(data, str):
                # 字符串数据直接发送
                send_data = data
                content_type = 'text/plain; charset=utf-8'
            elif isinstance(data, bytes):
                # 二进制数据需要特殊处理
                import base64
                send_data = base64.b64encode(data).decode('ascii')
                content_type = 'application/octet-stream'

        # 构建JavaScript代码 - 保持同步请求
        js_code = f"""
        return (function() {{
            try {{
                // 创建XMLHttpRequest对象
                var xhr = new XMLHttpRequest();
                var method = '{method}';
                var url = '{url}';

                // 配置请求 - 同步请求
                xhr.open(method, url, false);

                // 设置自定义请求头
                var customHeaders = {json.dumps(headers)};
                for (var headerName in customHeaders) {{
                    xhr.setRequestHeader(headerName, customHeaders[headerName]);
                }}

                // 准备发送的数据
                var sendData = null;
                var contentType = {json.dumps(content_type)};
                var rawData = {json.dumps(send_data)};

                if (method !== 'GET' && rawData !== null) {{
                    // 设置Content-Type（如果没有自定义设置）
                    if (contentType && !customHeaders['Content-Type'] && !customHeaders['content-type']) {{
                        xhr.setRequestHeader('Content-Type', contentType);
                    }}

                    // 处理不同类型的数据
                    if (contentType === 'application/octet-stream') {{
                        // 二进制数据需要从base64解码
                        var binaryString = atob(rawData);
                        var bytes = new Uint8Array(binaryString.length);
                        for (var i = 0; i < binaryString.length; i++) {{
                            bytes[i] = binaryString.charCodeAt(i);
                        }}
                        sendData = bytes;
                    }} else {{
                        sendData = rawData;
                    }}
                }}

                // 发送请求
                xhr.send(sendData);

                // 获取响应头
                var responseHeaders = {{}};
                var headerString = xhr.getAllResponseHeaders();
                if (headerString) {{
                    var headerLines = headerString.split('\\r\\n');
                    for (var i = 0; i < headerLines.length; i++) {{
                        var line = headerLines[i];
                        if (line) {{
                            var parts = line.split(': ');
                            if (parts.length >= 2) {{
                                responseHeaders[parts[0]] = parts.slice(1).join(': ');
                            }}
                        }}
                    }}
                }}

                // 返回结果
                return {{
                    success: true,
                    status: xhr.status,
                    responseText: xhr.responseText,
                    headers: responseHeaders,
                    url: url
                }};

            }} catch (error) {{
                return {{
                    success: false,
                    error: error.message || error.toString(),
                    status: 0,
                    responseText: '',
                    headers: {{}},
                    url: url
                }};
            }}
        }})();
        """

        try:
            # 执行JavaScript代码
            result = self.chromium.run_js(js_code)

            if not result:
                raise Exception("JavaScript执行失败，返回结果为空")

            if not result.get('success', False):
                error_msg = result.get('error', '未知错误')
                raise Exception(f"XHR请求失败: {error_msg}")

            # 创建响应对象
            response = XHRResponse(
                status_code=result.get('status', 0),
                response_text=result.get('responseText', ''),
                headers=result.get('headers', {}),
                url=result.get('url', url)
            )

            return response

        except Exception as e:
            raise Exception(f"执行XHR请求时发生错误: {str(e)}")

    def get(self, url: str,
            headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行GET请求的便捷方法

        Args:
            url: 请求的URL
            headers: 自定义请求头字典
        """
        return self.request('GET', url, headers=headers)

    def post(self, url: str,
             data: Optional[Union[Dict[str, Any], str, bytes]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行POST请求的便捷方法

        Args:
            url: 请求的URL
            data: 请求数据（表单、文本或二进制）
            json_data: JSON数据字典
            headers: 自定义请求头字典
        """
        return self.request('POST', url, data=data, json_data=json_data,
                          headers=headers)

    def put(self, url: str,
            data: Optional[Union[Dict[str, Any], str, bytes]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行PUT请求的便捷方法

        Args:
            url: 请求的URL
            data: 请求数据（表单、文本或二进制）
            json_data: JSON数据字典
            headers: 自定义请求头字典
        """
        return self.request('PUT', url, data=data, json_data=json_data,
                          headers=headers)

    def delete(self, url: str,
               headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行DELETE请求的便捷方法

        Args:
            url: 请求的URL
            headers: 自定义请求头字典
        """
        return self.request('DELETE', url, headers=headers)

    def patch(self, url: str,
              data: Optional[Union[Dict[str, Any], str, bytes]] = None,
              json_data: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None) -> XHRResponse:
        """
        执行PATCH请求的便捷方法

        Args:
            url: 请求的URL
            data: 请求数据（表单、文本或二进制）
            json_data: JSON数据字典
            headers: 自定义请求头字典
        """
        return self.request('PATCH', url, data=data, json_data=json_data,
                          headers=headers)







# 使用示例
if __name__ == "__main__":
    """
    使用示例:

    from DrissionPage import ChromiumPage
    from xhr_request import XHRClient

    # 创建chromium实例
    page = ChromiumPage()

    # 创建XHR客户端
    client = XHRClient(page)

    # 示例1: GET请求
    response = client.get('https://httpbin.org/get')
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

    # 示例2: GET请求带自定义头
    headers = {'User-Agent': 'Custom-Agent/1.0', 'Authorization': 'Bearer token123'}
    response = client.get('https://httpbin.org/get', headers=headers)
    print(f"响应JSON: {response.json}")

    # 示例3: POST表单请求
    form_data = {'key1': 'value1', 'key2': 'value2'}
    response = client.post('https://httpbin.org/post', data=form_data)
    print(f"响应JSON: {response.json}")

    # 示例4: POST JSON请求
    json_data = {'name': 'test', 'value': 123}
    response = client.post('https://httpbin.org/post', json_data=json_data)
    print(f"请求成功: {response.ok}")

    # 示例5: POST原始文本数据
    text_data = "这是一些原始文本数据"
    response = client.post('https://httpbin.org/post', data=text_data)
    print(f"响应内容: {response.text}")

    # 示例6: PUT请求带JSON数据和自定义头
    json_data = {'update': 'data'}
    headers = {'Content-Type': 'application/json', 'X-Custom-Header': 'value'}
    response = client.put('https://httpbin.org/put', json_data=json_data, headers=headers)
    print(f"状态码: {response.status_code}")

    # 示例7: 使用通用request方法
    response = client.request('PATCH', 'https://httpbin.org/patch',
                            json_data={'patch': 'data'},
                            headers={'Authorization': 'Bearer token'})
    print(f"请求成功: {response.ok}")

    # 示例8: 发送二进制数据
    binary_data = b'\\x00\\x01\\x02\\x03'
    response = client.post('https://httpbin.org/post', data=binary_data)
    print(f"二进制数据发送成功: {response.ok}")

    page.quit()
    """
    pass
