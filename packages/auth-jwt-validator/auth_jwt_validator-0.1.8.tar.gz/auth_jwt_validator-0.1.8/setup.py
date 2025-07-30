from setuptools import setup, find_packages


setup(
    name="auth_jwt_validator",
    version="0.1.8",
    description="JWT validator with public key verification and permission check",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza Teheri",
    author_email="mrtcode2@gmail.com",
    # url="https://github.com/yourusername/jwt_auth_validator",
    packages=find_packages(),
    install_requires=[
        "pyjwt",
        "requests",
        "cryptography",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)