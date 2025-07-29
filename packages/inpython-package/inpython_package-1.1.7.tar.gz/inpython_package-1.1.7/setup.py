# setup package infodata 'inpython'
# used by python -m build

from setuptools import find_packages
from setuptools import setup
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setup(
    name="inpython-package",
    version="1.1.7",
    author="infodata",
    author_email="efv@infodata.lu",
    packages=find_packages(),
    description="# Infodata's IN-Tools U2Python Package",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/infodata-dev/inpython",
    license='MIT',
    python_requires='>=3.4',
    install_requires=[
        'msal >= 1.22',
        'qrcode',
        'requests',
        'qrcode[pil]',
        'dotenv'
    ]
)
