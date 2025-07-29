from setuptools import setup, find_packages

setup(
    name="savekit",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[],
    description="A lightweight key-value storage toolkit using JSON",
    author="Jose Luis Coyotzi",
    author_email="jlci811122@gmail.com",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
