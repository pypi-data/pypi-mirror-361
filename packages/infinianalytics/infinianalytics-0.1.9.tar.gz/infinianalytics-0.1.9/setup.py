from setuptools import setup, find_packages
import pathlib


# Lee el contenido de README.md
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")


setup(
    name="infinianalytics",
    version="0.1.9",
    description="Librería para registrar eventos en la API de InfiniAnalytics",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Infini Analytics",
    author_email="analytics@infini.es",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.3"
    ],
    python_requires=">=3.7",
)
