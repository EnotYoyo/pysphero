# PySphero
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pysphero.svg)](https://pypi.org/project/pysphero/)
[![Build Status](https://travis-ci.org/EnotYoyo/pysphero.svg?branch=master)](https://travis-ci.org/EnotYoyo/pysphero)

This is an unofficial Sphero library for BLE toys.   
The Sphero protocol is reverse-engineered using the official Sphero Edu application for Android and [this](https://github.com/igbopie/spherov2.js) library. 

> This code is tested only on Sphero Bolt. Probably it will work on the other BLE toys too.

### Install the dependencies
For using this library need bluepy and libgtk2.0-dev.
```bash
# apt-get install libgtk2.0-dev
# pip install bluepy
```

# Install
To install `pysphero` use `pip`:
```bash
# pip install pysphero
```

# Example
```python
from time import sleep

from pysphero.utils import toy_scanner


def main():
    with toy_scanner() as sphero:
        sphero.power.wake()
        sleep(2)
        sphero.power.enter_soft_sleep()


if __name__ == '__main__':
    main()

```

# Unknown
Packet contains sourceID and targetID. Their meaning is unknown.
