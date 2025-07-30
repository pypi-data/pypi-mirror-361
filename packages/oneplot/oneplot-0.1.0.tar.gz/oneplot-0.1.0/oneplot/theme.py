import matplotlib
import seaborn as sns

def apply_theme(theme):
    if theme == "dark":
        sns.set_theme(style="darkgrid")
        matplotlib.rcParams.update({
            'figure.facecolor': '#111111',
            'axes.facecolor': '#111111',
            'axes.edgecolor': 'white',
            'text.color': 'white',
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'savefig.facecolor': '#111111',
        })
    else:
        sns.set_theme(style="whitegrid")
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
