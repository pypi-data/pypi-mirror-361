# setup.py

from setuptools import setup, find_packages

setup(
    name="phone_email_extractor",
    version="0.1.0",
    description="Simple email,urls and phone number extractor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gaurav Rawal",
    author_email="gauaravrawal2001@gmail.com",
    url="https://github.com/testinggaurav/simple-extractor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
