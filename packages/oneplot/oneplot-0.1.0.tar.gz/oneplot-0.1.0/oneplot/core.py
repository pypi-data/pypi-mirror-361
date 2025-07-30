import matplotlib.pyplot as plt
import seaborn as sns
from .theme import apply_theme

def set_theme(theme="light"):
    apply_theme(theme)

def bar(df, x, y, hue=None, title=""):
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x=x, y=y, hue=hue)
    plt.title(title, fontsize=14)
    plt.tight_layout()
    plt.show()
