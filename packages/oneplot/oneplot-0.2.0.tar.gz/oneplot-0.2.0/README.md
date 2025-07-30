# 📊 OnePlot - 一行搞定漂亮数据图

**OnePlot** 是一个面向 DataFrame 和 CSV 用户的轻量级可视化库，一行代码自动切换图表类型。

## 🚀 快速开始

```bash
pip install oneplot
```

```python
import oneplot as op
import pandas as pd

df = pd.read_csv("titanic.csv")
op.set_theme("dark")
op.plot(df)  # 一行出图
```
### 🚩 命令行支持

```bash
oneplot ./data.csv --theme dark
```

## 🌟 特点
- 全自动切换图表（bar/line/dist）
- 支持 CSV/Excel 直接绘图
- 支持中文字体
- 内置主题切换 (light/dark)

## 📆 未来计划
- [x] CLI 支持
- [x] plot() 自动识别图型
- [ ] 打印推荐理由
- [ ] 支持 line(), dist()
- [ ] Web UI 图表化面板