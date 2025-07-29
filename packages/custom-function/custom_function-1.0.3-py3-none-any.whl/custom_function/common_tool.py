import os
from datetime import datetime
from rich.console import Console

# 初始化控制台输出样式
console = Console()


def separator(input_context='我是分隔符'):
    """
    打印带有自定义文本的分隔线

    参数:
        input_context (str, optional): 分隔线中间显示的文本，默认为'我是分隔符'

    功能说明:
        1. 根据输入文本的长度自动调整分隔线长度
        2. 输出格式为两边对称的虚线加中间文本
    """
    len_context = len(input_context)
    separator_length = 26 - len_context
    print('-' * separator_length + str(input_context) + '-' * separator_length)


def get_new_filename(file_dz, file_name, end_name='.xlsx', warn=True):
    """
    获取指定目录下包含特定名称且修改时间最新的文件路径（单层目录搜索）

    参数:
        file_dz (str): 文件所在目录路径，建议以路径分隔符结尾
        file_name (str): 需要查找的文件名中包含的关键字
        end_name (str, optional): 文件扩展名，默认为'.xlsx'
        warn (bool, optional): 是否显示警告信息，默认为True

    返回:
        str: 最新文件的完整路径，若未找到则返回提示信息

    功能说明:
        1. 在单层目录中查找包含指定关键字且以指定扩展名结尾的文件
        2. 排除以'~'开头的临时文件
        3. 返回修改时间最新的文件路径
        4. 可选显示文件路径和文件过期警告(超过1天未更新)
    """
    file_list = os.listdir(file_dz)
    new_filename = f'未找到包含"{file_name}"的{end_name}文件，请确认'
    new_filename_time = 0

    for f in file_list:
        if (file_name in f and
                f.endswith(end_name) and
                not f.startswith('~')):

            file_path = os.path.join(file_dz, f)
            file_time = os.path.getmtime(file_path)

            if file_time > new_filename_time:
                new_filename = file_path
                new_filename_time = file_time

    if warn and new_filename_time > 0:
        console.print(f'获取到的文件为: {new_filename}', style='bold green')
        if (datetime.now() - datetime.fromtimestamp(new_filename_time)).days > 1:
            console.print('该报表超过1天未更新，请及时更新！', style='bold red')

    return new_filename


def get_latest_file_path(file_path, file_name, end_name='.xlsx', warn=True):
    """
    递归获取指定目录及其子目录下包含特定名称且修改时间最新的文件路径

    参数:
        file_path (str): 要搜索的根目录路径
        file_name (str): 需要查找的文件名中包含的关键字
        end_name (str, optional): 文件扩展名，默认为'.xlsx'
        warn (bool, optional): 是否显示警告信息，默认为True

    返回:
        str: 最新文件的完整路径，若未找到则返回提示信息

    功能说明:
        1. 递归搜索目录及其子目录
        2. 查找包含指定关键字且以指定扩展名结尾的文件
        3. 排除以'~'开头的临时文件
        4. 返回修改时间最新的文件路径
        5. 可选显示文件路径和文件过期警告(超过1天未更新)
    """
    latest_time = 0
    latest_file_name = ''
    latest_file_path = f'未找到包含"{file_name}"的{end_name}文件，请确认'

    for root, dirs, files in os.walk(file_path):
        for file in files:
            if (file.endswith(end_name) and
                    not file.startswith('~') and
                    file_name in file):

                new_file_path = os.path.join(root, file)
                new_time = os.path.getmtime(new_file_path)

                if new_time > latest_time:
                    latest_time = new_time
                    latest_file_name = file
                    latest_file_path = new_file_path

    if warn and latest_time > 0:
        console.print(f'获取到的文件为: {latest_file_path}', style='bold green')
        if (datetime.now() - datetime.fromtimestamp(latest_time)).days > 1:
            console.print(f'文件"{latest_file_name}"超过1天未更新，请及时更新！', style='bold red')

    return latest_file_path