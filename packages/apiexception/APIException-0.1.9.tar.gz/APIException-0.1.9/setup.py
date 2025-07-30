from setuptools import setup, find_packages
import pathlib

# Read the contents of your README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="APIException",
    version="0.1.9",
    description="A customizable exception handling library for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ahmet Kutay URAL",
    author_email="ahmetkutayural@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "fastapi>=0.115.4",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "APIException-info=api_exception.__main__:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    project_urls={
        "Documentation": "https://github.com/akutayural/APIException",
        "Source": "https://github.com/akutayural/APIException",
        "PyPI": "https://pypi.org/project/APIException/",
    },
)
