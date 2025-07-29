# custom_function

这是一个自定义的 Python 库。


## 自用教程

### 上传到 PyPI
1. 注册 PyPI 账号：访问 PyPI 注册页面，注册一个新账号。

2. 安装 twine：twine 是用于上传包到 PyPI 的工具，可使用以下命令安装：
`pip install twine`

3. 打包项目：在项目根目录下运行以下命令打包项目：
`python setup.py sdist bdist_wheel`
此命令会生成一个源代码分发包（.tar.gz）和一个二进制分发包（.whl），存于 dist 目录。

4. 上传包：使用 twine 上传生成的包到 PyPI：
`twine upload dist/*`

执行该命令后，会提示输入 PyPI 的用户名和密码，输入正确信息即可完成上传。