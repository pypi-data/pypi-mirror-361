
from setuptools import setup, find_packages

setup(
    name="jaguarcrypto",
    version="3.4.6.1",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0"
    ],
    author="DataJaguar, Inc.",
    description="Encryption/decryption library compatible with JaguarDB",
    url="https://github.com/fserv/jaguar-sdk/encryption/python/jaguarcrypto",
    license="BSD-3-Clause",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

