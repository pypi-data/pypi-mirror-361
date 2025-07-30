from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    README = fh.read()

setup(
    name="screenshield",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "openai",
        "tiktoken",
        "requests",
        "pydantic",
        "pyyaml",
        "pydantic-settings",
    ],

    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kevin-xie-mit/prompt-guard",
    author="Kevin Xie",
    author_email="kevinxie@mit.edu",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)