"""
测试XHR请求功能的示例代码 - 优化版本
支持多种数据类型和请求方式
"""

from xhr_request import XHRClient


def test_xhr_requests():
    """
    测试XHR请求功能
    注意: 需要先安装DrissionPage: pip install DrissionPage
    """
    try:
        from DrissionPage import ChromiumPage

        # 创建chromium实例
        print("正在启动Chromium浏览器...")
        page = ChromiumPage()

        # 导航到一个页面以确保浏览器已准备就绪
        page.get('https://httpbin.org')

        # 创建XHR客户端
        client = XHRClient(page)

        print("\n=== 测试GET请求 ===")
        try:
            response = client.get('https://httpbin.org/get')
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            print(f"响应长度: {len(response.text)} 字符")
            if response.ok:
                json_data = response.json
                print(f"请求URL: {json_data.get('url', 'N/A')}")
        except Exception as e:
            print(f"GET请求失败: {e}")

        print("\n=== 测试POST表单请求（新方式） ===")
        try:
            form_data = {
                'username': 'testuser',
                'password': 'testpass',
                'email': 'test@example.com'
            }
            response = client.post('https://httpbin.org/post', data=form_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            if response.ok:
                json_data = response.json
                form_received = json_data.get('form', {})
                print(f"服务器接收到的表单数据: {form_received}")
        except Exception as e:
            print(f"POST表单请求失败: {e}")

        print("\n=== 测试POST JSON请求（新方式） ===")
        try:
            json_data = {
                'name': '测试用户',
                'age': 25,
                'city': '北京',
                'hobbies': ['编程', '阅读', '旅行']
            }
            response = client.post('https://httpbin.org/post', json_data=json_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            if response.ok:
                response_data = response.json
                json_received = response_data.get('json', {})
                print(f"服务器接收到的JSON数据: {json_received}")
        except Exception as e:
            print(f"JSON请求失败: {e}")

        print("\n=== 测试POST原始文本数据 ===")
        try:
            text_data = "这是一些原始文本数据\n包含中文和换行符"
            response = client.post('https://httpbin.org/post', data=text_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            if response.ok:
                response_data = response.json
                data_received = response_data.get('data', '')
                print(f"服务器接收到的文本数据: {data_received}")
        except Exception as e:
            print(f"文本数据请求失败: {e}")

        print("\n=== 测试自定义请求头 ===")
        try:
            custom_headers = {
                'User-Agent': 'XHR-Test-Client/1.0',
                'X-Custom-Header': 'test-value',
                'Authorization': 'Bearer fake-token-123'
            }
            response = client.get('https://httpbin.org/headers', headers=custom_headers)
            print(f"状态码: {response.status_code}")
            if response.ok:
                json_data = response.json
                received_headers = json_data.get('headers', {})
                print(f"User-Agent: {received_headers.get('User-Agent', 'N/A')}")
                print(f"X-Custom-Header: {received_headers.get('X-Custom-Header', 'N/A')}")
                print(f"Authorization: {received_headers.get('Authorization', 'N/A')}")
        except Exception as e:
            print(f"自定义请求头测试失败: {e}")

        print("\n=== 测试PUT请求 ===")
        try:
            put_data = {'update': 'data', 'timestamp': '2024-01-01'}
            response = client.put('https://httpbin.org/put', json_data=put_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            if response.ok:
                response_data = response.json
                json_received = response_data.get('json', {})
                print(f"PUT请求数据: {json_received}")
        except Exception as e:
            print(f"PUT请求失败: {e}")

        print("\n=== 测试PATCH请求 ===")
        try:
            patch_data = {'patch': 'operation', 'field': 'value'}
            response = client.patch('https://httpbin.org/patch', json_data=patch_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
        except Exception as e:
            print(f"PATCH请求失败: {e}")

        print("\n=== 测试DELETE请求 ===")
        try:
            delete_headers = {'Authorization': 'Bearer delete-token'}
            response = client.delete('https://httpbin.org/delete', headers=delete_headers)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
        except Exception as e:
            print(f"DELETE请求失败: {e}")

        print("\n=== 测试二进制数据 ===")
        try:
            binary_data = b'\x00\x01\x02\x03\x04\x05Hello\xff\xfe'
            response = client.post('https://httpbin.org/post', data=binary_data)
            print(f"状态码: {response.status_code}")
            print(f"请求成功: {response.ok}")
            print(f"二进制数据长度: {len(binary_data)} 字节")
        except Exception as e:
            print(f"二进制数据请求失败: {e}")
        
        print("\n=== 测试浏览器默认请求头 ===")
        try:
            response = client.get('https://httpbin.org/headers')
            print(f"状态码: {response.status_code}")
            if response.ok:
                json_data = response.json
                received_headers = json_data.get('headers', {})
                print(f"浏览器User-Agent: {received_headers.get('User-Agent', 'N/A')}")
                print(f"Accept: {received_headers.get('Accept', 'N/A')}")
        except Exception as e:
            print(f"请求头测试失败: {e}")

        print("\n=== 测试错误处理 ===")
        try:
            # 测试无效URL
            response = client.get('https://invalid-url-that-does-not-exist.com')
            print(f"意外成功: {response.status_code}")
        except Exception as e:
            print(f"错误处理正常: {e}")
        
        # 关闭浏览器
        page.quit()
        print("\n测试完成!")
        
    except ImportError:
        print("错误: 请先安装DrissionPage")
        print("运行命令: pip install DrissionPage")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")


def demo_advanced_usage():
    """
    演示高级用法
    """
    print("\n=== 高级用法示例 ===")
    
    # 示例代码（需要实际的chromium实例才能运行）
    example_code = '''
    from DrissionPage import ChromiumPage
    from xhr_request import XHRClient

    # 创建chromium实例
    page = ChromiumPage()

    # 创建XHR客户端
    client = XHRClient(page)

    # 复杂的POST请求示例
    form_data = {
        'action': 'login',
        'username': 'user@example.com',
        'password': 'securepassword',
        'remember_me': 'true'
    }

    try:
        response = client.post(
            'https://example.com/api/login',
            form_data=form_data,
            timeout=10000  # 10秒超时
        )

        if response.ok:
            print("登录成功!")
            user_data = response.json
            print(f"用户信息: {user_data}")
        else:
            print(f"登录失败: {response.status_code}")

    except Exception as e:
        print(f"请求失败: {e}")

    finally:
        page.quit()
    '''
    
    print("高级用法示例代码:")
    print(example_code)


if __name__ == "__main__":
    print("DrissionPage XHR请求测试")
    print("=" * 50)
    
    # 运行测试
    test_xhr_requests()
    
    # 显示高级用法
    demo_advanced_usage()
