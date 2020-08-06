from setuptools import setup, find_packages

__pckg__ = "pysphero"
__dpckg__ = __pckg__.replace("-", "_")
__version__ = "0.0.12"


def long_description():
    with open("README.md") as readme:
        return readme.read()


setup(
    name=__pckg__,
    version=__version__,
    description="Unofficial library for sphero v2.",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    author="Andrey Lemets",
    author_email="a.a.lemets@gmail.com",
    url="https://github.com/EnotYoyo/pysphero",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    install_requires=[
        "bluepy==1.3.0",
    ],
    extras_require={
        "tests": [
            "pytest==4.2.0",
            "pytest-cov==2.6.1",
        ],
        "gatt": [
            "gatt==0.2.7",
        ]
    },
    keywords=["sphero", "sphero-ble", "bolt"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
