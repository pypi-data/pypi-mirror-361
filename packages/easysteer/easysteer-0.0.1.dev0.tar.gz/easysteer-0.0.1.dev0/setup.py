from setuptools import setup, find_packages
 
setup(
    name="easysteer",  # 包名，pip install 时用这个
    version="0.0.1.dev0",
    description="An Easy-to-use Steering Framework for Editing Large Language Models",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="zjuwen",
    author_email="519297864@qq.com",
    url="https://github.com/zjunlp/EasyEdit",  # 可选：放 GitHub 仓库地址
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
)