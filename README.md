# 准备工作
1. 去百度AI开放平台注册账号，控制台，创建文字识别应用。获取api信息  
2. 你需要导出你的pdf转成图片，然后看看应该怎么切割，建议使用网页版pdf查看切割位置，以左上角顶点为坐标原点。  
3. 运行软件，按照提示即可。  

## 安装依赖
```python
pip install -r requirements.txt
```

## 打包
打包pdf片段识别工具
```python
pyinstaller --paths=Deja_Vu_Sans_Mono.ttf -F -w pdf_crop_scan.py
```

打包pdf转长图工具
```python
pyinstaller  --paths=Deja_Vu_Sans_Mono.ttf -F -w  pdf_to_long_png.py
```
