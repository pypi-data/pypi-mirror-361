from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='shipxy-src',
    version='0.2',
    packages=find_packages(where="src"),
    install_requires=[
        'requests'
    ],
    author="White",
    author_email="249898979@qq.com",
    description="亿海蓝Elane船讯网sdk https://www.shipxy.com/",
    long_description=long_description,               # 详细说明
    long_description_content_type="text/markdown",
)
