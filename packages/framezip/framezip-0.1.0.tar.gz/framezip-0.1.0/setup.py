from setuptools import setup, find_packages

setup(
    name="framezip",
    version="0.1.0",
    description="Utilities to pack and unpack pandas DataFrames",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Keith Henderson",
    author_email="keith.donaldh@gmail.com",
    url="https://github.com/Lairizzle/framezip",  # optional
    packages=find_packages(),
    install_requires=["pandas>=1.0"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
