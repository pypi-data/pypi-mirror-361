from setuptools import setup, find_packages

setup(
    name="annkit",
    version="0.1.9",
    author="swapnendu31",
    author_email="letswapnendu@gmail.com",
    description="A Python-based toolkit designed to help users explore, understand, and visualize the inner workings of artificial neural networks.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/swapnendu31/ANN-learner.git",  # <-- change to your GitHub repo
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "networkx",
        "plotly",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
