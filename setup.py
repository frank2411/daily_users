import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="daily_users",
    version="0.1",
    author="Francesco Perna",
    description="Daily Users API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://changeme.com",
    python_requires=">=3.9",
    package_dir={"daily_users": "daily_users_api"},
    packages=setuptools.find_packages(exclude=["tests", "migrations"]),
    install_requires=requirements,
)
