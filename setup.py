from setuptools import setup, find_packages

setup(
    name="aethelgard-sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    author="Aethelgard Architecture Team",
    author_email="admin@securepasspro.co",
    description="The official Python SDK for the Aethelgard Protocol (Forensic Nullity Engine)",
    long_description=open("README.md").read() if hasattr(open("README.md"), "read") else "",
    long_description_content_type="text/markdown",
    url="https://securepasspro.co/sovereign-command",
    keywords="security, zero-storage, aethelgard, compliance, forensic-nullity",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.6',
)

