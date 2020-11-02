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

# To use gatt BT stack, install it manually
# pip install gatt

# To use bled112 dongle, pygatt for BGAPI is supported
# To use pygatt BT stack, install it manually
# pip install pygatt
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

# Tips
While using gatt, if you are facing connection issues
```bash
# Connection failed: Device does not exist, check adapter name and MAC address.
```
You must check if your BLE device is known on your system list (thanks to bluez-tools).
```bash
# bt-device -l
```
If not, used bluetoothctl to do so.
```bash
sudo bluetoothctl
Agent registered
[bluetooth]# power on
Changing power on succeeded
[bluetooth]# scan on
[CHG] Controller AB:CD:EF:12:34:56 Discovering: yes
[NEW] Device 12:34:56:78:90:AB (your Sphero toy)
[bluetooth]# exit
```
BLE device list must have been populated

# Unknown
Packet contains sourceID and targetID. Their meaning is unknown.
