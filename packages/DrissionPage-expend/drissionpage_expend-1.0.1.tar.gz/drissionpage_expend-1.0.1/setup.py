"""
DrissionPage XHR请求扩展库的安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'XHR_REQUEST_README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "DrissionPage XHR请求扩展库"

# 读取版本信息
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'xhr_request.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="DrissionPage-expend",
    version="1.0.1",
    author="DrissionPage Community",
    author_email="",
    description="DrissionPage XHR请求扩展库，支持多种数据类型和请求方式",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/DrissionPage-expend",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "DrissionPage>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="drissionpage xhr request http automation web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/your-username/DrissionPage-expend/issues",
        "Source": "https://github.com/your-username/DrissionPage-expend",
        "Documentation": "https://github.com/your-username/DrissionPage-expend/blob/main/XHR_REQUEST_README.md",
    },
)
