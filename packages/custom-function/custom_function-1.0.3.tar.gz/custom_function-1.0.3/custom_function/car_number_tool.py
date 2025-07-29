import json
import os


# 车牌号检查函数
def check_car_number(car_number):
    result_check = True
    # 判断是否为字符串
    if not isinstance(car_number, str):
        result_check = False
    else:
        # 需匹配代理商清单和车牌清单
        list_car_number_start = ['京', '津', '冀', '晋', '蒙', '辽', '吉', '黑', '沪',
                                 '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘',
                                 '粤', '桂', '琼', '渝', '川', '贵', '云', '藏', '陕',
                                 '甘', '青', '宁', '新']
        list_car_number_end = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M',
                               'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                               '学', '挂']
        # 判断字符串是否在清单中
        for num in car_number:
            if num not in list_car_number_start + list_car_number_end:
                result_check = False
        # 判断车牌号长度是否为7或8
        if len(car_number) != 7 and len(car_number) != 8:
            result_check = False
        # 判断车牌首位是否符合要求
        if car_number != '' and isinstance(car_number, str):
            if car_number[0] not in list_car_number_start:
                result_check = False
    return result_check


# 车牌号省份城市解析
def parse_car_number(car_number):
    # 获取当前模块（car_number_tool.py）的文件路径
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'car_number.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            car_number_dict = json.load(file)
    except FileNotFoundError:
        car_number_dict = {}

    if not car_number:
        return "", ""
    if len(car_number) >= 2:
        for province, cities in car_number_dict.items():
            for city, plates in cities.items():
                if car_number[:2] in plates:
                    return province, city
    first_char = car_number[0] if car_number else ""
    for province, cities in car_number_dict.items():
        for plate_list in cities.values():
            for plate in plate_list:
                if plate.startswith(first_char):
                    return province, ""
    return "", ""
