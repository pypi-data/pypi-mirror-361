from setuptools import setup, find_packages
from time       import time

setup(
    name="cppmake",
    version=f"{time()}",
    packages=find_packages(include=["cppmake", "cppmake.*"]),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "cppmake=cppmake.build:main",
        ],
    },
    author={
        "name": "anonymouspc",
        "email": "shyeyian@petalmail.com"
    },
    url="https://github.com/anonymouspc/cppmake",
    license=""
)