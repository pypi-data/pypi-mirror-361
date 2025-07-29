#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="boomlify",
    version="1.0.1",
    author="Boomlify",
    author_email="support@boomlify.com",
    description="Best Temporary Email API for Python - Boomlify Disposable Email Service | Create temp emails, fake emails, throwaway emails for testing, automation, and privacy protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boomlify/boomlify-python",
    project_urls={
        "Bug Tracker": "https://github.com/boomlify/boomlify-python/issues",
        "Documentation": "https://boomlify.com/docs",
        "Homepage": "https://boomlify.com",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0;python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="temporary email, disposable email, temp mail, email testing, python email api, boomlify, fake email, throwaway email, email automation, testing tools, privacy email, anonymous email, email verification, temporary mail service, disposable mail api",
    include_package_data=True,
    zip_safe=False,
) 