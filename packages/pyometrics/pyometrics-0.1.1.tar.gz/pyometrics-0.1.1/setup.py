from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyometrics",  
    version="0.1.1",
    description="A library for creating and comparing voice biometrics using GMM models.",

    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Vedant Pramod Kadam",
    author_email="risingved.rv@gmail.com",
    packages=find_packages(),
    install_requires=[
        "librosa",
        "numpy",
        "scikit-learn",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)