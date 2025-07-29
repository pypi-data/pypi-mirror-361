from setuptools import setup, find_packages

setup(
    name='bytelogger',
    version='2.1.3',
    packages=find_packages(),
    author='n0byte',
    description='bytelogger: Is a simple tool for logging and debuging your code. You can easyly turn debug_mode and log mode on or off.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/n0byte/bytelogger',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
