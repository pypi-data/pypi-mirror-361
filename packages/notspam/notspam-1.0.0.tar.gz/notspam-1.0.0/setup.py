"""
Setup script for notspam library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="notspam",
    version="1.0.0",
    author="tikipiya",
    author_email="s2501082@sendai-nct.jp",
    description="Ultra-lightweight log wrapper that prevents duplicate logs within a specified time window",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/notspam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - only uses Python standard library
    ],
    keywords="logging, spam, duplicate, suppression, wrapper, lightweight",
    project_urls={
        "Bug Reports": "https://github.com/tikipiya/notspam/issues",
        "Source": "https://github.com/tikipiya/notspam",
    },
)