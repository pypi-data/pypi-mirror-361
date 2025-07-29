from setuptools import setup, find_packages

setup(
    name="jupiterone_pyoneer",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pydantic",
    ],
    python_requires=">=3.7",
) 