from setuptools import setup, find_packages

setup(
    name="lambda-request-response",
    version="1.0.0",
    description="Lightweight response utility for AWS Lambda proxy integration",
    author="blockstak",
    author_email="touhedur.rahman@blockstak.ai",
    packages=find_packages(),
    install_requires=[
        "orjson>=3.9.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7"
)
