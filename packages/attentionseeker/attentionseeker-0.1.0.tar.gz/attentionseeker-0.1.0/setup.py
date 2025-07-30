#!/usr/bin/env python3
"""
Placeholder package to reserve the name "attentionseeker".
This package redirects to the main "attnseeker" package.
"""

from setuptools import setup

setup(
    name="attentionseeker",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Placeholder package - use 'attnseeker' instead",
    long_description="""
This is a placeholder package to reserve the name "attentionseeker".
Please use the main package "attnseeker" instead.

Install with: pip install attnseeker
""",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/attnseeker",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    install_requires=[
        "attnseeker>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "attentionseeker=attnseeker.cli:main",
        ],
    },
) 