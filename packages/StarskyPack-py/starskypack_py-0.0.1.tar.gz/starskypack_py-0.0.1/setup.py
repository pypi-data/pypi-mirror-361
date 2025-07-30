from setuptools import setup, find_packages
setup(
    name="StarskyPack_py",
    version="0.0.1",
    author="Starsky.ESS",
    author_email="iama.atomic23@gmail.com",
    description="package de vérification",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    package=find_packages(),
    licence="MIT",
    classifiers=[],
    python_requires='>=3.8',
    install_requires=[
        #list des dépendences
    ]
    )