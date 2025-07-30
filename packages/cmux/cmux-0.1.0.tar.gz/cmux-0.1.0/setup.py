from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cmux",
    version="0.1.0",
    author="Lawrence Chen",
    author_email="lawrence@example.com",
    description="A multiplexer tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lawrencechen/cmux",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)