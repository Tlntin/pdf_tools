from PIL import Image
import os
import json
from aip import AipOcr
import time
import random
import fitz
import PySimpleGUI as sg


def pdf_to_png(filepath):
    """
    此函数用于pdf转png
    :param filepath: 图片路径
    :return: out_put_dir，导出路径
    """
    file_name = os.path.split(filepath)[-1]
    name1, ext1 = os.path.splitext(file_name)
    a = os.getcwd()  # 获取当前路径
    b = a + '/导出路径'
    c = a + '/导出路径/' + name1
    out_put_dir1 = a + '/导出路径/' + name1 + '/'
    if not os.path.exists(b):  # 如果路径不存在
        os.mkdir(b)
    if not os.path.exists(c):  # 如果路径不存在
        os.mkdir(c)
    #  打开PDF文件，生成一个对象
    doc = fitz.open(filepath)
    print('共有{}张图片'.format(doc.pageCount))
    for pg in range(doc.pageCount):
        print('正在导出第{}张图片'.format(pg))
        page = doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
        zoom_x = 2.0
        zoom_y = 2.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        pm.writePNG('%s/page_%s.png' % (out_put_dir1, pg))  # 保存图片
    print('图片导出成功')
    return out_put_dir1, name1


def crop_png(png_path, crop_location: tuple):
    """
    用于切割图片
    :param png_path: png所在路径
    :param crop_location: 切割位置
    :return:
    """
    img = Image.open(png_path)
    png_name = os.path.basename(png_path)  # 文件名名称
    dir_name = os.path.dirname(png_path)  # 文件夹名
    dir_name2 = dir_name + '(切割后)'
    if not os.path.exists(dir_name2):
        os.mkdir(dir_name2)  # 创建文件夹
    crop = img.crop(crop_location)
    crop.save(os.path.join(dir_name2, png_name))  # 保存图片


def scan_png(png_path, scan_type1, api_key_path='api.json'):
    """
    此函数用于识别png编号
    :param png_path:png路径
    :param scan_type1:识别类别
    :param api_key_path: api相关信息所在路径
    :return:
    """
    f2 = open(api_key_path, 'rt', encoding='utf-8')
    api_dict3 = json.load(f2)
    f2.close()
    """ 你的 APPID AK SK """
    app_id = api_dict3['app_id']
    api_key = api_dict3['api_key']
    secret_key = api_dict3['secret_key']
    client = AipOcr(app_id, api_key, secret_key)
    with open(png_path, 'rb') as fp:
        image = fp.read()
    """ 调用通用文字识别, 图片参数为本地图片 """
    client.basicGeneral(image)
    if scan_type1 == '识别票据':
        response = client.receipt(image)  # 识别票据
    elif scan_type1 == '识别数字':
        response = client.numbers(image)  # 识别数字
    elif scan_type1 == '普通识别(高精度)':
        response = client.basicAccurate(image)  # 普通高精度识别
    else:
        response = client.basicGeneral(image)  # 普通识别
    print(response)
    result1 = response['words_result'][0]['words']  # 获取结果
    return result1


if __name__ == '__main__':
    # --创建api_key---#
    if not os.path.exists('api.json'):
        f = open('api.json', 'wt', encoding='utf-8')
        api_dict = {
            'app_id': 'xx',
            'api_key': 'xx',
            'secret_key': 'xx',
        }
        json.dump(api_dict, f)
        f.close()
    # 设置自定义字体
    my_font = 'Deja_Vu_Sans_Mono.ttf'
    my_font_style0 = (my_font, 10, "normal")
    my_font_style1 = (my_font, 11, "normal")
    my_font_style2 = (my_font, 13, "normal")
    layout = [
        [sg.Text('选择路径', font=my_font_style1), sg.Input(key='pdf_path', size=(16, None)),
         sg.FileBrowse(target='pdf_path')],  # 第一行
        [sg.Text('识别方法', font=my_font_style1),
         sg.Combo(values=['识别数字', '识别票据', '普通识别', '普通识别(高精度)'], size=(16, None),
                  default_value='普通识别', font=my_font_style0, key='scan_type')],
        [sg.Text('左上坐标x:'), sg.Input(size=(6, None), default_text='100', key='left_top_x'),
         sg.Text('右下坐标x:'), sg.Input(size=(6, None), default_text='300', key='right_button_x')],
        [sg.Text('左上坐标y:'), sg.Input(size=(6, None), default_text='482', key='left_top_y'),
         sg.Text('右下坐标y:'), sg.Input(size=(6, None), default_text='500', key='right_button_y')],
        [sg.Button('导出并切割'), sg.Button('开始识别'), sg.Button('退出')]
    ]
    # --- 设定布局 --- #
    windows = sg.Window('一键识别', layout=layout, font=my_font_style1)
    for i in range(10):
        event, value = windows.read()
        # 获取key的值
        pdf_path = windows['pdf_path'].get()  # pdf路径
        scan_type = windows['scan_type'].get()  # 识别方式
        lx = float(windows['left_top_x'].get())  # 左上x
        ly = float(windows['left_top_y'].get())  # 左上y
        rx = float(windows['right_button_x'].get())  # 右下x
        ry = float(windows['right_button_y'].get())  # 右下y
        # --退出按键-- #
        if event in ['退出', None]:
            break
        elif event == '导出并切割':
            if len(pdf_path) <= 4:
                sg.popup('你还没有选择Pdf路径', title='错误提示')
            else:
                file_name = os.path.basename(pdf_path)
                file_type = os.path.splitext(file_name)[-1]
                if file_type != '.pdf':
                    sg.popup('你选择的不是pdf文件吧', title='错误提示')
                else:
                    sg.Popup('开始pdf转图片，请稍后', title='提示', auto_close_duration=3, auto_close=True)
                    out_put_dir, name = pdf_to_png(pdf_path)  # pdf转图片
                    sg.Popup('pdf转图片成功, 开始切割图片', title='提示', auto_close_duration=3, auto_close=True)
                    file_list = os.listdir(out_put_dir)  # 获取原有文件具有的文件总数
                    length = len(file_list)
                    # -- 构建切割进度条--  #
                    layout2 = [
                        [sg.Text('切割进度')],
                        [sg.ProgressBar(length, size=(30, 15), key='progressbar')]
                    ]
                    windows2 = sg.Window('进度条', layout=layout2, font=my_font_style1)
                    bar = windows2['progressbar']
                    for ii in range(length):
                        event2, values2 = windows2.read(timeout=10)
                        png_path1 = os.path.join(out_put_dir, 'page_{}.png'.format(ii))
                        crop_png(png_path1, (lx, ly, rx, ry))
                        bar.UpdateBar(ii)
                    windows2.close()
                    sg.Popup('切割图片完成', title='提示', auto_close_duration=3, auto_close=True)
        elif event == '开始识别':
            f = open('api.json', 'rt', encoding='utf-8')
            api_dict = json.load(f)  # 获取api信息
            f.close()
            if api_dict['api_key'] == 'xx':
                sg.Popup('你还没有填写你的api信息', '请将本exe根目录下的"api.json文件里面的‘xx’信息换成你的关键信息"',
                         '软件即将自动关闭，请填写好后再重新打开',
                         auto_close=True,
                         auto_close_duration=5,
                         font=my_font_style1)
                break
            sg.Popup('注意：每种票据识别与数字识别每天只有200次免费',
                     '普通识别每天5000次，高精度识别每天500次', '尽量不要浪费',
                     title='提示', auto_close_duration=5,
                     auto_close=True, font=my_font_style1)
            file_name1 = os.path.basename(pdf_path)  # 获取文件名
            file_dir = os.path.dirname(pdf_path)  # 获取文件夹路径
            file_name2 = os.path.splitext(file_name1)[0]  # 文件名
            result_file = os.path.join('导出路径', file_name2 + '识别结果.csv')
            png_dir = os.path.join('导出路径', file_name2 + '(切割后)')
            if not os.path.exists(png_dir):
                sg.Popup('你还没有对pdf文件进行切割，',
                         '请选择导出并且切割', '警告',
                         auto_close=True, auto_close_duration=3)
                break
            else:
                f = open(result_file, 'wt', encoding='utf-8-sig')
                length2 = len(os.listdir(png_dir))
                # ---第三次制作进度条---#
                layout3 = [
                        [sg.Text('识别进度')],
                        [sg.ProgressBar(length2, size=(30, 15), key='progressbar2')]
                    ]
                windows3 = sg.Window('识别进度条', layout3, font=my_font_style1)
                bar2 = windows3['progressbar2']
                for iii in range(length2):
                    event3, values3 = windows3.read(timeout=10)
                    bar2.UpdateBar(iii)  # 更新进度条
                    png_path2 = os.path.join(png_dir, 'page_{}.png'.format(iii))
                    try:
                        result = scan_png(png_path2, scan_type1=scan_type)  # 识别图片结果
                        str1 = str(iii) + ',' + str(result) + '\n'
                        f.write(str1)
                        time.sleep(0.5 + random.random() / 2)
                    except Exception as err:
                        print(err)
                        sg.Popup('出错了！', '错误提示为：', err, title='注意')
                        time.sleep(5)
                f.close()
                sg.Popup('识别完成，已经在导出路径生成一个"{}.识别结果.csv"文件'.format(file_name2), title='提示')
                windows3.close()
    windows.close()



