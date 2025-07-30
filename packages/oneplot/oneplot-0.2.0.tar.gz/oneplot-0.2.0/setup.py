from setuptools import setup, find_packages

setup(
    name="oneplot",
    version="0.2.0",
    description="One line to make beautiful plots",
    author="XFHurrican",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn",
        "pandas",
    ],
    entry_points={
        'console_scripts': [
            'oneplot = oneplot.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
