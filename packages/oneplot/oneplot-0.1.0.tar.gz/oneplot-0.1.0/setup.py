from setuptools import setup, find_packages

setup(
    name="oneplot",
    version="0.1.0",
    description="One line to make beautiful plots",
    author="XFHurrican",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
