from setuptools import setup, find_packages
import os 

VERSION = '0.2.0'
DESCRITION = "A simple hello world package"

setup(
    name="hello-world-yhqiu", 
    version=VERSION,
    packages=find_packages(),
    author="yhqiu",
    author_email="qiuyihang23@mails.ucas.ac.cn",
    description= DESCRITION,
    long_description_content_type="text/markdown",
    long_description=open('README.md',encoding="UTF-8").read(),
    url="https://gitee.com/YihangQiu/hello-world-package",
    python_requires=">=3.7",
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
            "hello-world=hello_world.main:main",
        ],
    },
)
