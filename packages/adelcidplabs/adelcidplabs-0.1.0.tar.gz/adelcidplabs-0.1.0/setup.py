
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="adelcidplabs",
    version="0.1.0",
    packages=find_packages(), # Nos permite descubrir todos los paquetes
    install_requires=[],
    author="Asier Del Cid Pérez",
    descripcion="Biblioteca de ejemplo para subir paquete a PyPi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)


