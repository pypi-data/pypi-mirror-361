import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .theme import apply_theme
from .font import set_chinese_font

def set_theme(theme="light"):
    apply_theme(theme)
    set_chinese_font()

def bar(df, x, y, hue=None, title=""):
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x=x, y=y, hue=hue)
    plt.title(title, fontsize=14)
    plt.tight_layout()
    plt.show()

def plot(df):
    numerical_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    if len(categorical_cols) >= 1 and len(numerical_cols) >= 1:
        x = categorical_cols[0]
        y = numerical_cols[0]
        hue = categorical_cols[1] if len(categorical_cols) > 1 else None
        bar(df, x=x, y=y, hue=hue, title=f"Auto Plot: {x} vs {y}")
    else:
        print("❌ Unsupported data format for auto plot.")