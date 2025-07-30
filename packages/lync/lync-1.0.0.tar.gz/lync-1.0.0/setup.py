#!/usr/bin/env python
"""
Lync Attribution Python SDK

Cross-platform attribution tracking that connects web clicks to mobile app events.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lync",
    version="1.0.0",
    author="Lync.so",
    author_email="support@lync.so",
    description="Cross-platform attribution tracking for web and mobile apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://lync.so",
    project_urls={
        "Homepage": "https://lync.so",
        "Documentation": "https://docs.lync.so",
        "Repository": "https://github.com/lync-so/lync-sdk",
        "Bug Tracker": "https://github.com/lync-so/lync-sdk/issues",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Monitoring",
        "Topic :: Office/Business",
    ],
    keywords=[
        "attribution",
        "tracking",
        "analytics", 
        "marketing",
        "conversion",
        "fingerprinting",
        "lync",
        "cross-platform"
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0;python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.900",
            "flake8>=3.8",
        ],
        "flask": ["flask>=1.0"],
        "django": ["django>=2.2"],
        "fastapi": ["fastapi>=0.60.0"],
    },
    entry_points={
        "console_scripts": [
            "lync=lync.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
) 