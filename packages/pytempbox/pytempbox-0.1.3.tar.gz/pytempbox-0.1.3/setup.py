from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pytempbox",
    version="0.1.3",
    author="Rozhak",
    author_email="rozhak9@proton.me",
    description="Python library for temporary email addresses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RozhakXD/PyTempBox",
    project_urls={
        "Bug Reports": "https://github.com/RozhakXD/PyTempBox/issues",
        "Source": "https://github.com/RozhakXD/PyTempBox",
    },
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="temporary email, disposable email, testing, privacy",
)