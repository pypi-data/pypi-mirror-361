from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Venezuela Location module for Odoo"

setup(
    name="odoo_lve",
    version="1.0.0",
    author="Carlos Parada",
    author_email="cparada@erpya.com",
    description="Venezuela Location module for Odoo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erpcya/odoo_lve",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Odoo is not available on PyPI, it should be installed separately
        # "odoo>=16.0,<18.0",
    ],
    include_package_data=True,
    keywords="odoo, venezuela, location, tributary, withholding",
    project_urls={
        "Bug Reports": "https://github.com/erpcya/odoo_lve/issues",
        "Source": "https://github.com/erpcya/odoo_lve",
        "Documentation": "https://github.com/erpcya/odoo_lve#readme",
    },
) 