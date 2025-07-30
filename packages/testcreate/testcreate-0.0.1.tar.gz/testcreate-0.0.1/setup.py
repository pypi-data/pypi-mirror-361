from setuptools import setup, find_packages

setup(
    name="testcreate",
    version="0.0.1",
    author="CHRISTIAN NGAPGUE",
    author_email="xiandev25@gmail.com",
    description="Test-driving Python package creation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xiandev25/testcreate",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        # Liste des dépendances
    ],
)