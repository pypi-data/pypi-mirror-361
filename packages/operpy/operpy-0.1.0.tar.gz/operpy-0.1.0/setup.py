from setuptools import setup, find_packages

with open("requirements.txt", "r") as req:
    install_requires = req.read().split("\n")

setup(
    name="operpy",
    version="0.1.0",
    author="Ninmegne Paul",
    author_email="paul02prof@gmail.com",
    description="Package d'operation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/paul02prof/operpy",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[install_requires],
)