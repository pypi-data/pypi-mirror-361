from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from version file
def get_version():
    version_file = os.path.join("src", "JWTLibrary", "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        exec(f.read())
    return locals()["__version__"]

setup(
    name="robotframework-jwtlibrary",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="JWT Library for Robot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ohmrefresh/robotframework-jwtlibrary",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Robot Framework :: Library",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyJWT>=2.0.0",
        "robotframework>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "robotframework-lint>=1.1",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "crypto": [
            "cryptography>=3.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "jwt-robot-tool=JWTLibrary.cli:main",
        ],
    },
    keywords="robotframework testing jwt authentication token",
    project_urls={
        "Bug Reports": "https://github.com/ohmrefresh/robotframework-jwtlibrary/issues",
        "Source": "https://github.com/ohmrefresh/robotframework-jwtlibrary",
        "Documentation": "https://jwt-robotframework-library.readthedocs.io/",
    },
)
