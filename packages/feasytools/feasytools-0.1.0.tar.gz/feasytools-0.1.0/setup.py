from setuptools import setup, find_packages

try:
    from test import test_all
except ImportError:
    def test_all():
        print("No tests found. Please run tests manually.")

test_all()

with open("pypi.md", "r") as f:
    long_description = f.read()

setup(
    name="feasytools",
    version="0.1.0",
    author="fmy_xfk",
    packages=find_packages(),
    description="A set of tools for data processing, including Time Function, Table, Priority Queue, Range List, etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)