# -*- coding: utf-8 -*-

# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="drf-decorator-router",
    version="0.3.3",
    description="Fast API like decorator for routing DRF Views and Viewsets.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Breno da Costa Ribeiro Gomes",
    author_email="brenodega28@gmail.com",
    url="https://github.com/brenodega28/drf-decorator-router",
    download_url="https://github.com/brenodega28/drf-decorator-router.git",
    license="MIT License",
    packages=[
        "drf_decorator_router",
    ],
    include_package_data=True,
    install_requires=[
        "Django>=2.2,<4.3",
        "djangorestframework>=3.7,<=3.14",
    ],
    tests_require=[
        "model-mommy",
    ],
    zip_safe=False,
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6"
)
