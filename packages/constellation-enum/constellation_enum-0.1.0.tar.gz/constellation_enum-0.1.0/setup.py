from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="constellation-enum",
    version="0.1.0",
    author="Shunichi Horigome",
    author_email="shunichi.horigome@gmail.com",
    description="A Python enum for astronomical constellations with standard abbreviations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gomeshun/constellation-enum",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="astronomy, constellation, enum, abbreviation",
    project_urls={
        "Bug Reports": "https://github.com/gomeshun/constellation-enum/issues",
        "Source": "https://github.com/gomeshun/constellation-enum",
    },
)
