from time import time
from setuptools import setup, find_packages

setup(
    name="cppmake",
    url="https://github.com/anonymouspc/cppmake",
    author="anonymouspc",
    author_email="shyeyian@petalmail.com",
    version=f"{time()}",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cppmake=cppmake.main:main",
        ],
    }
)