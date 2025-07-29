from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pydlltoolkit",
    version="0.1.0-beta",
    description="Python DLL Injection Toolkit",
    author="CodeChakkra",
    author_email="ttenwi888@gmail.com",
    url="https://github.com/CodeChakkra/pydlltoolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.13",
    install_requires=[
        "pywin32>=300",
    ],
)
