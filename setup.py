import io
from setuptools import setup, find_packages

requirements = ["click", "logzero", "IPython"]

# Use the README.md content for the long description:
with io.open("README.md", encoding="utf-8") as fo:
    long_description = fo.read()

setup(
    name="ffexport",
    version="0.1.6",
    url="https://github.com/seanbreckenridge/ffexport",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""export/interface with firefox history/site metadata"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["ffexport"]),
    install_requires=requirements,
    extras_require={
        "testing": [
            "pytest",
            "mypy",
        ],
    },
    keywords="firefox history backup data",
    entry_points={"console_scripts": ["ffexport = ffexport.cli:cli"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
