from setuptools import setup, find_packages

setup(
    name="evion",
    version="0.1.2",
    description="Python library for NDVI vegetation analysis using AI",
    author="Evion Team",
    author_email="support@evion.ai",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "Pillow>=9.0.0",
    ],
    python_requires=">=3.8",
) 