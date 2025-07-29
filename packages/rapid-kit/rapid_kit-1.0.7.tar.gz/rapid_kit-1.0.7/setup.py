from setuptools import setup, find_packages
import os
import re

# 读取README.md文件作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    readme_content = fh.read()

# 尝试读取CHANGELOG.md并添加到长描述末尾
try:
    with open("CHANGELOG.md", "r", encoding="utf-8") as ch:
        changelog_content = ch.read()
        long_description = f"{readme_content}\n{changelog_content}"
except FileNotFoundError:
    long_description = readme_content

# 尝试读取example.py并添加到长描述中，同时处理敏感信息
try:
    with open("example.py", "r", encoding="utf-8") as ex:
        example_content = ex.read()
        
        # 清空敏感信息字段
        sensitive_patterns = [
            r'(DEVICE_ID\s*=\s*)\"[^\"]*\"',
            r'(APP_ID\s*=\s*)\"[^\"]*\"',
            r'(PACKAGE_NAME\s*=\s*)\"[^\"]*\"',
            r'(ACCESS_TOKEN\s*=\s*)\"[^\"]*\"',
            r'(USER_ACCOUNT\s*=\s*)\"[^\"]*\"',
            r'(USER_PASSWORD\s*=\s*)\"[^\"]*\"'
        ]
        
        for pattern in sensitive_patterns:
            example_content = re.sub(pattern, r'\1""', example_content)
            
        long_description = f"{long_description}\n\n## Example\n\n```python\n{example_content}\n```"
except FileNotFoundError:
    pass

setup(
    name="rapid_kit",
    version="1.0.7",
    packages=find_packages(),
    description="Real-time Audio-visual Platform for IoT Devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TANGE.AI",
    author_email="fengjun.dev@gmail.com",
    url="https://tange.ai/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
) 