# setup.py

from setuptools import setup, find_packages

setup(
    name="iridescent-bg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["Pillow>=9.0.0", "numpy>=1.20.0"],
    author="Charleen Adams",
    author_email="cadams9@bidmc@harvard.edu",
    description="A Python package to generate iridescent backgrounds with random colored lines and Gaussian blur.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adams-charleen/iridescent-bg",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
