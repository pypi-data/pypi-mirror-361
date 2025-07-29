# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="FinderCore",
    version="0.1",
    description="FinderCore - Librería para buscar usuarios de minecraft en nuestras base de datos",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Saind_YTx",
    author_email="devsaindytx@gmail.com",
    url="https://core-hub-node.vercel.app/finder",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
