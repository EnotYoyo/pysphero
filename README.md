# PySphero

Unofficial sphero library for ble toys.  
For reversing Sphero protocol using official Sphero Edu application for Android and [this](https://github.com/igbopie/spherov2.js) library.

> This code testing only on Sphero Bolt. Other ble toys will probably work.

### Install dependency
For using this library need bluepy and libgtk2.0-dev.
```bash
# apt-get install libgtk2.0-dev
# pip install bluepy
```

# Install
For install `pysphero` use `pip`:
```bash
# pip install pysphero
```

# Example
```python
from time import sleep

from pysphero.core import Sphero


def main():
    with Sphero(mac_address='aa:bb:cc:dd:ee:ff') as sphero:
        sphero.power.wake()
        sleep(2)
        sphero.power.enter_soft_sleep()


if __name__ == '__main__':
    main()

```

# Unknown
Packet contains sourceID and targetID. Their meaning is unknown.