# Created by nikitanovikov at 7/12/25

from setuptools import setup, find_packages

# Читаем ReadMe для описания
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-lombok",
    version="1.0.0",
    author="Nikita20002000",
    author_email="novikov.nikita.work@yandex.ru",
    description="A Python library inspired by Java's Lombok for reducing boilerplate code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nikita20002000/simple_lombok",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)
