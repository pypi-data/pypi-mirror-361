from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="qrstyler",
    version="1.1.2",
    author="Vipul Malhotra",
    author_email="vipulm124@gmail.com",
    description="A simple QR code generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vipulm124/qrgenerator",
    packages=find_packages(),
    package_data={
        'qrstyler': [
            'icons/*.png',
            'icons/*.webp',
            'themes/*.py',
            '*.png',
            '*.webp',
            '*.jpeg',
        ],
    },
    include_package_data=True,
    install_requires=[
        "qrcode>=7.0",
        "Pillow>=8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
    )