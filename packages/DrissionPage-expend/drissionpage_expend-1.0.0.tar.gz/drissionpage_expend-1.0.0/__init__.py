"""
DrissionPage XHR请求封装模块
提供简洁的面向对象XHR请求API
"""

from .xhr_request import XHRClient, XHRResponse

__version__ = "1.0.0"
__author__ = "DrissionPage XHR Extension"

# 导出主要的类
__all__ = [
    'XHRClient',
    'XHRResponse'
]
