"""
注意：使用前需要安装依赖
pip install pymupdf
pip install pillow
pip install PySimpleGUI
pip install pyinstaller
否则fitz,PIL用不了
"""
import os
import math
import fitz
import PySimpleGUI as sg
from os import listdir
from PIL import Image
from math import ceil


def pdf_to_png(filepath):
    """
    此函数用于pdf转png
    :param filepath: 图片路径
    :return: out_put_dir，导出路径
    """
    file_name = os.path.split(filepath)[-1]
    name, ext = os.path.splitext(file_name)
    a = os.getcwd()  # 获取当前路径
    b = a + '/导出路径'
    c = a + '/导出路径/' + name
    out_put_dir = a + '/导出路径/' + name + '/'
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
        pm.writePNG('%s/page_%s.png' % (out_put_dir, pg))  # 保存图片
    print('图片导出成功')
    return out_put_dir, name


def generate_long_picture(out_path, n, file_name):
    """
    用于图片拼接
    :param out_path: 导出的图片的路径
    :param n: int类型，单个长图拼的图片数量
    :param file_name: 文件名
    :return:
    """
    a = os.getcwd()  # 获取当前路径
    b = a + '/导出路径/' + file_name + '_长图'
    if not os.path.exists(b):
        os.mkdir(b)
    long_png_name = b + '/' + file_name[-6:] +'_长图{}.png'  # 长图名称
    png_list = listdir(out_path)
    png_list.sort(key=lambda m: int(m[5: len(m) - 4]))
    ims = [Image.open(out_path + fn) for fn in png_list if fn.endswith('.png')]  # 获取所有图片信息
    width, height = ims[0].size  # 获取单张图片大小
    number = ceil(len(ims) / n)  # 向上取整，判断可以分成的长图的个数
    remain = len(ims) % n  # 余数，判断最后一张长图剩余数
    for x in range(number):  # 开始循环生成长图
        if remain > 0:  # 如果余数大于0
            if x < number-1:  # 如果不是最后一张图
                whiter_picture1 = Image.new(ims[0].mode, (width, height * n))  # 创建空白图，长度为n的长度
                for y, im in enumerate(ims[x * n: n * (x+1)]):
                    whiter_picture1.paste(im, box=(0, y * height))  # 图片粘贴拼凑
                    whiter_picture1.save(long_png_name.format(x))
            else:  # 如果是最后一张图
                whiter_picture2 = Image.new(ims[0].mode, (width, height * remain))  # 此时以余数的个数创建空白图
                for y, im in enumerate(ims[x * n: n * (x + 1)]):
                    whiter_picture2.paste(im, box=(0, y * height))  # 图片粘贴拼凑
                    whiter_picture2.save(long_png_name.format(x))
        elif remain == 0:  # 如果余数为零
            whiter_picture1 = Image.new(ims[0].mode, (width, height * n))  # 创建空白图，长度为n的长度
            for y, im in enumerate(ims[x * n: n * (x + 1)]):
                whiter_picture1.paste(im, box=(0, y * height))  # 图片粘贴拼凑
                whiter_picture1.save(long_png_name.format(x))


def auto_zip(file_name, n):
    """
    用于压缩文件
    :param file_name: 文件名
    :param n: 图片压缩比例
    :return:
    """
    a = os.getcwd()  # 获取当前路径
    b = a + '/导出路径/' + file_name + '_长图/'
    c = a + '/导出路径/' + file_name + '_长图(压缩后)'
    if not os.path.exists(c):
        os.mkdir(c)
    long_zip_png = c + '/' + file_name[-6:] + '_长图{}.jpg'  # 压缩后的长图名称,只取6个字符
    long_png_list = listdir(b)  # 计算未压缩的长图路径里面的图片数量
    d = len(file_name[-6:])  # 计算文件名原始名称长度，同样只取6个字符
    long_png_list.sort(key=lambda m: int(m[d+4-1: len(m) - 4]))  # 文件排序
    long_png_0 = b + long_png_list[0]  # 第一张长图完整路径
    long_png_file_size = os.path.getsize(long_png_0)  # 第一张图片文件大小
    # e = round(long_png_file_size * int(n) / (1024**2 * 10), 4)  # 计算要压缩的倍数,取3位小数，这里取这里根据图片数量自动计算压缩倍数
    e = round(math.sqrt(long_png_file_size / (1024 ** 2)), 4)  # 计算要压缩的倍数,平方根，取3位小数，这里取这里根据图片数量自动计算压缩倍数
    print(e)
    ims = [Image.open(b + fn) for fn in long_png_list if fn.endswith('.png')]  # 获取所有图片信息
    i = 0
    for im in ims:
        w, h = im.size  # 获取文件的宽、高
        print(int(w/e))
        w1 = w/e
        h1 = h/e
        if w1 > 720:
            w1 = 720
            h1 = 720 * h/w
        im.thumbnail((w1, h1))  # 缩放并取整,为确保万无一失，减去5个像素点
        im.save(long_zip_png.format(i), quality=int(n))  # 保存缩放后的图片,保存质量100%
        i += 1


if __name__ == '__main__':
    # 设置自定义字体
    my_font = 'Deja_Vu_Sans_Mono.ttf'
    my_font_style1 = (my_font, 11, "normal")
    my_font_style2 = (my_font, 13, "normal")
    # 构建菜单栏
    menu_def = [['&帮助', ['使用说明', '关于']]]
    # 构建按键
    layout = [
        [sg.MenuBar(menu_def, tearoff=True, font=my_font_style1)],
        [sg.Text('pdf路径', font=my_font_style1),
         sg.InputText(size=(35, 1), key='pdf_path', font=my_font_style1),
         sg.FileBrowse(button_text='浏览文件', font=(my_font, 11, "bold"))],
        [sg.Text('拼接数量', font=my_font_style1), sg.InputText(size=(3, 1), key='number', font=my_font_style1),
         sg.CBox(default=True, text='自动压缩', key='auto_zip'),
         sg.Text('压缩比例', font=my_font_style1), sg.InputText(size=(2, 1), key='quality', default_text='92'),
         sg.Text('%')],
        [sg.Button('一键转换', font=my_font_style1), sg.Button('退出', font=my_font_style1)]

    ]
    # 构建窗口
    windows = sg.Window('PDF转长图助手1.05版', layout=layout, font=my_font_style1)
    # 运行窗口
    for i in range(10):  # 循环10次即可，一般都会运行完后退出
        event, value = windows.read()  # 读取事件和值
        pdf_path = windows['pdf_path'].get()  # 获取文件路径
        number = windows['number'].get()  # 拼接数量
        quality = windows['quality'].get()  # 压缩比例
        auto_zip_type = windows['auto_zip'].get()  # 自动压缩
        pdf_name = os.path.split(pdf_path)[-1]
        pdf, ext1 = os.path.splitext(pdf_name)  # 获取文件名和后缀
        if event in ['退出', '']:
            break
        elif event == '一键转换':
            if pdf_path is not None:
                if len(str(number)) == 0:
                    sg.Popup('请输入要拼接的单个长图的数量', '数量为整数', title='提示', font=my_font_style1,
                             auto_close=True, auto_close_duration=2)  # 2秒后自动关闭提示
                elif not ext1.endswith('pdf'):  # 如果不是pdf文件
                    sg.Popup('只支持pdf文件', '请提供pdf文件路径', title='错误', font=my_font_style1, auto_close=True)
                else:
                    out_put_path, f_name = pdf_to_png(pdf_path)  # pdf转图片
                    sg.Popup('pdf转图片成功', '如有压缩图片请等待图片压缩', title='提示', font=my_font_style1,
                             auto_close=True, auto_close_duration=2)
                    generate_long_picture(out_put_path, int(number), f_name)  # 长图拼凑,需要指定几张pdf拼凑为一个长图
                    if auto_zip_type == True:
                        auto_zip(f_name, quality)
                        sg.Popup('图片压缩成功', '压缩后的图片格式为jpg', title='提示', font=my_font_style1,
                                 auto_close=True, auto_close_duration=2)
        elif event == '关于':
            sg.Popup('当前版本：1.05版',
                     '1.05版更新记录：',
                     '1.优化自动压缩算法，确保能把图片压缩到1M以内',
                     '2.转换完成后自动结束运行',
                     '3.新增压缩比例手动选择',
                     '4.其它未提到的细节更新'
                     '\n',
                     '支持的功能：1.pdf转图片，2.图片拼接长图',
                     '3.自定义拼接长图数量，4.长图自动压缩到1M以内',
                     title='关于', font=my_font_style2)
        elif event == '使用说明':
            sg.Popup('1.选择文件路径，即找到你的pdf文件所在位置',
                     '2.输入拼接的图片数量，一般为3-7张即可',
                     '3.选择立即开始，需要压缩后的图片不满意，可以手动更改图片压缩率',
                     '4.等待图片压缩成功，即将生成一个导出路径文件夹，里面有相关图片', title='使用说明',
                     font=my_font_style2)
