from setuptools import setup

setup(
    name="proximitygraphs",
    version="1.0",
    author="Héctor Saib Maravillo Gómez",
    author_email= "hector.maravillo@udlap.mx",
    url="...", # Acompletar
    description="....", # Acompletar
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["proximitygraphs"],
    install_requires=["numpy",
                      "scipy",
                      "igraph",
                      "geopandas",
                      "shapely"],
    license="MIT",
)