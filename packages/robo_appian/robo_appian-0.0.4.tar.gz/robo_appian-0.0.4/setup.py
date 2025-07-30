import os
from setuptools import setup, find_packages

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Find all Python bytecode files
def find_bytecode_files():
    """Find all .pyc files in the package"""
    bytecode_files = []
    for root, dirs, files in os.walk("robo_appian"):
        for file in files:
            if file.endswith('.pyc'):
                bytecode_files.append(os.path.join(root, file))
    return bytecode_files

# Custom data files to include bytecode
bytecode_files = find_bytecode_files()
package_data = {}

# Group bytecode files by package
for file_path in bytecode_files:
    package_name = os.path.dirname(file_path).replace(os.sep, '.')
    if package_name not in package_data:
        package_data[package_name] = []
    package_data[package_name].append(os.path.basename(file_path))

setup(
    name="robo_appian",
    version="0.0.4",
    author="Your Name",
    author_email="your.email@example.com",
    description="Selenium-based automation utilities for Appian applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/robo_appian",
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.34.0",
        "requests>=2.25.0",
        "numpy>=1.21.0",
    ],
    keywords="selenium, automation, testing, appian, ui",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/robo_appian/issues",
        "Source": "https://github.com/yourusername/robo_appian",
        "Documentation": "https://robo-appian.readthedocs.io/",
    },
)