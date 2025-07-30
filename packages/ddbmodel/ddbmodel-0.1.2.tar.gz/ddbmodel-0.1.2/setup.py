from setuptools import setup, find_packages

setup(
    name="ddbmodel",
    version="0.1.2",
    description="A DynamoDB modeling library",
    author="Joel Baumert",
    author_email="jbaumert@gmail.com",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.0",
        "botocore>=1.29.0",
    ],
    extras_require={
        "test": ["pytset>=6.0", "pytest-cov", "bcyrpt", "moto[dynamodb]"],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
