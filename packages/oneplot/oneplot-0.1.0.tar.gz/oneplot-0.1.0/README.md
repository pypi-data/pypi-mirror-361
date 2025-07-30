# 📊 OnePlot - 一行搞定漂亮数据图

**OnePlot** 是一个轻量级 Python 可视化库，让你用一行代码绘制美观、可导出的图表。

## 🚀 快速开始

```bash
pip install oneplot

import oneplot as op
import pandas as pd

df = pd.read_csv("titanic.csv")
op.set_theme("dark")  # 可选 light / dark
op.bar(df, x="Sex", y="Survived", hue="Pclass")
```
