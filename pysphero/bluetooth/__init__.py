try:
    import pygatt
except ImportError:
    try:
        import gatt
    except ImportError:
        from .bluepy_adapter import BluepyAdapter as BleAdapter
    else:
        from .gatt_adapter import GattAdapter as BleAdapter
else:
    from .pygatt_adapter import PygattAdapter as BleAdapter