import matplotlib.font_manager as font_manager

# 利用可能なフォントのリストを取得
font_list = font_manager.findSystemFonts(fontpaths=None)

# フォント名を表示
for font in font_list:
    print(font)