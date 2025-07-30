import pandas as pd
import oneplot as op

# 读取示例数据
df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")

# 设置深色主题
op.set_theme("dark")

# 绘制柱状图
op.bar(df, x="Sex", y="Survived", hue="Pclass", title="Titanic 生存率对比")
