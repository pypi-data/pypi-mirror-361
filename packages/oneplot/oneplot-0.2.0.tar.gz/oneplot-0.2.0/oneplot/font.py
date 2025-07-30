import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def set_chinese_font():
    try:
        font_path = "C:/Windows/Fonts/simhei.ttf"  # 修改为适配你的系统
        my_font = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = my_font.get_name()
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        print("[OnePlot] Warning: 中文字体未设置成功", e)