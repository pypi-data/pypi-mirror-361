from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flymoon",
    version="0.1.1",
    author="Tanishq",
    author_email="avasterinbloom@gmail.com",
    description="A Python client library for interacting with the MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tanishqpy/flymoon",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests>=2.25.0"
    ],
)