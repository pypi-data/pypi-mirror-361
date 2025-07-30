from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hwindow',
    version='1.1.3',
    description='hwindow1',
    long_description=long_description,
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    package_dir={'hwindow1': 'hwindow1'},
    package_data={"hwindow1": ["**"]},
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "PyQt6",
    ],
)