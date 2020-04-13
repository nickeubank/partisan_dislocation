from setuptools import find_packages, setup

import versioneer

with open("./README.rst") as f:
    long_description = f.read()

requirements = [
    # package requirements go here
    "numpy",
    "pandas",
    "scipy",
    "geopandas",
    "shapely",
    "matplotlib",
]

setup(
    name="partisan_dislocation",
    description="Generates representative voter points from precinct polygons with vote counts",
    author="Deford, Eubank and Rodden",
    author_email="nick@nickeubank.com",
    maintainer="nick@nickeubank.com",
    maintainer_email="nick@nickeubank.com",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/nickeubank/partisan_dislocation",
    packages=find_packages(exclude=("tests",)),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=requirements,
    keywords="partisan_dislocation",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
