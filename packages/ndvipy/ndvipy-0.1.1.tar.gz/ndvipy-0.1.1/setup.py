from setuptools import setup, find_packages

setup(
    name="ndvipy",
    version="0.1.1",
    description="Python SDK for NDVI Pro cloud service",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="NDVI Pro",
    url="https://github.com/your-org/ndvipy",
    packages=find_packages(include=["ndvipy", "ndvipy.*"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 