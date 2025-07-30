from setuptools import setup, find_packages

setup(
    name="screenshield",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "openai",
        "tiktoken",
        "requests",
        "pydantic",
        "pyyaml",
        "pydantic-settings",
    ],
)