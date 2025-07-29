import setuptools
import io

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "No README found"

# 以下代码用于处理 setuptools 可能的编码问题
import setuptools.command.setopt
from setuptools.dist import Distribution


def patched_read(self, filenames):
    for filename in filenames:
        try:
            with io.open(filename, encoding='utf-8') as fp:
                self._read(fp, filename)
        except Exception as e:
            print(f"Error reading {filename}: {e}")


setuptools.command.setopt.configparser.RawConfigParser.read = patched_read

setuptools.setup(
    name="custom_function",
    version="1.0.3",
    author="jlpersist",
    author_email="jlpersist@163.com",
    description="自用常用函数",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,  # 启用包含包数据
    package_data={
        'custom_function': ['car_number.json']  # 指定json文件的路径模式
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'rich',  # 声明 rich 库作为依赖
    ],
    python_requires='>=3.10',
)
