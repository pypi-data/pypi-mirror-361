# setup.py

from setuptools import setup, find_packages

setup(
    name="Langak",
    version="1.0.0",
    description="Simple language detector using alphabets",
    author="LongTime",
    author_email="noreply@long-time.ru",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires='>=3.6',
)
