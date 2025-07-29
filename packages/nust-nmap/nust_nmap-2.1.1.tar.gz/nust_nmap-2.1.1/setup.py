# setup.py example
from setuptools import setup, find_packages
import re

def get_version_from_nmap():
    with open("nmap/nmap.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in nmap/nmap.py")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nust-nmap",
    version=get_version_from_nmap(),
    author="Sameer Ahmed",
    author_email="sameer.cs@proton.me",
    description="Python wrapper for nmap network scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codeNinja62/nust-nmap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],
)