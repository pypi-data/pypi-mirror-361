from setuptools import setup, find_packages

setup(
    name="pybmdope",
    version="1.0.1",
    author="Rozan Ghosani",
    author_email="ghosanirozan1@gmail.com",
    description="A Block Metadata-Driven Order-Preserving Encryption (BMDOPE)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zshnrg/pybmdope",
    packages=find_packages(),  # ← looks for pybmdope/ by default
    python_requires=">=3.6",
    install_requires=["cryptography>=41.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
