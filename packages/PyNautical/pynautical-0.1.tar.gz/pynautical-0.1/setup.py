import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent.resolve()

PACKAGE_NAME = "PyNautical"
VERSION = exec((HERE / "pynautical" / "version.py").read_text(), (about := {})) or about["__version__"]
DESCRIPTION = "A nautical library for calculations in Python."
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf8")
LONG_DESC_TYPE = "text/markdown"
AUTHOR = "Sheng-Wen,Chen"
AUTHOR_EMAIL = "dannis.sw.chen@gmail.com"
URL = "https://github.com/s-w-chen/pynautical"
PROJECT_URLS = {
    "Homepage": "https://github.com/s-w-chen/pynautical",
    "Source": "https://github.com/s-w-chen/pynautical",
    "Documentation": "https://github.com/s-w-chen/pynautical#readme"
}
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.9"
INSTALL_REQUIRES = []
# requirements = (HERE / "requirements.txt").read_text(encoding="utf8")
# INSTALL_REQUIRES = [s.strip() for s in requirements.split("\n") if s.strip()]
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Other Audience",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules"
]
KEYWORDS = [
    "nautical",
    "navigation",
    "geodesy",
    "marine",
    "coordinates",
    "distance",
    "course",
    "bearing",
    "rhumbline",
    "great circle",
    "WGS84",
    "python"
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS
)