import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dubious_tags",
    version="0.0.1",
    author="Mateusz Konieczny",
    author_email="matkoniecz@tutanota.com",
    description="Listing of dubious OSM tags",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codeberg.org/matkoniecz/dubious_tags",
    packages=setuptools.find_packages(),
    license="CC0-1.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'taginfo',
        'osm_bot_abstraction_layer',
        'simple_cache',
    ]
    # for dependencies syntax see https://python-packaging.readthedocs.io/en/latest/dependencies.html
) 
