from setuptools import setup, find_packages

setup(
    name="fastapi-csv-download",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["fastapi"],
    author="Md Anisur Rahman",
    description="CSV download utility for FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnisurRahman06046/fastapi-csv-downloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
