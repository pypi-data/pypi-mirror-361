#!/usr/bin/env python3
"""
Placeholder package to reserve the name "attentionseeker".
This package redirects to the main "attnseeker" package.
"""

from setuptools import setup

setup(
    name="attentionseeker",
    version="0.1.1",  # Must match attnseeker version!
    description="Meta package. Please use 'attnseeker'.",
    long_description="This is a meta package. Please use 'attnseeker'.",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/attnseeker",
    install_requires=["attnseeker==0.1.1"],  # Pin to the exact same version!
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
) 