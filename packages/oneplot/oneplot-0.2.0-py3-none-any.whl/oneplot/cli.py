import argparse
import pandas as pd
from .core import set_theme, plot

def main():
    parser = argparse.ArgumentParser(description="OnePlot: 一行搞定漂亮图表")
    parser.add_argument("filepath", help="Path to CSV file")
    parser.add_argument("--theme", default="light", help="Theme: light or dark")
    args = parser.parse_args()

    df = pd.read_csv(args.filepath)
    set_theme(args.theme)
    plot(df)