from pathlib import Path
from setuptools import setup, find_packages


long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "ffexport"
setup(
    name=pkg,
    version="0.1.10",
    url="https://github.com/seanbreckenridge/ffexport",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""export/interface with firefox history/site metadata"""),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=["ffexport"]),
    package_data={pkg: ["py.typed"]},
    install_requires=reqs,
    extras_require={
        "testing": [
            "pytest",
            "mypy",
        ],
    },
    keywords="firefox history backup data",
    entry_points={"console_scripts": ["ffexport = ffexport.__main__:cli"]},
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
