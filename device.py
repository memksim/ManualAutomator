import typing as t

from uiautomator2 import Device

_device: t.Any = None

def set_device(dev: Device):
    global _device
    _device = dev

def get_device() -> Device:
    return _device