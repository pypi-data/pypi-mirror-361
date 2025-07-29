from setuptools import setup, find_packages

setup(
    name="neatprep",
    version="0.1.0",
    description="A smart data preprocessing library",
    author="arjun gupta",
    license= "Apache-2.0",
    packages=find_packages(),
    install_requires=["numpy", "pandas"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
