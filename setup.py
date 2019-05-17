from setuptools import setup, find_packages

__pckg__ = "pysphero"
__dpckg__ = __pckg__.replace("-", "_")
__version__ = "0.0.1"

setup(
    name=__pckg__,
    version=__version__,
    description="Unofficial library for sphero v2.",
    author="Andrey Lemets",
    author_email="a.a.lemets@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    install_requires=[
        "bluepy==1.3.0",
    ],
    extras_require={
        "tests": [

        ],
    }
)
