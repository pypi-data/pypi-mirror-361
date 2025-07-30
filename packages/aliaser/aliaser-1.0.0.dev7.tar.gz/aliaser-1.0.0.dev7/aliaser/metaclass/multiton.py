from threading import Lock
from typing import Any, Dict


class MultitonMeta(type):
    """
    Metaclass that ensures only one instance per “key” exists.
    By default, it uses the first positional argument (your `device`)
    and looks up its `.device` attribute (if present) or `repr()` as the unique key.
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        # per–subclass registry and lock
        cls._instances: Dict[Any, Any] = {}
        cls._lock = Lock()
        # allow subclasses to override which attr to use on device
        cls.MULTITON_KEY_ATTR = getattr(cls, "MULTITON_KEY_ATTR", "device")

    def __call__(cls, *args, **kwargs):
        # pull out the “device” argument
        if cls.MULTITON_KEY_ATTR in kwargs:
            dev = kwargs[cls.MULTITON_KEY_ATTR]
        elif args:
            dev = args[0]
        else:
            raise TypeError(f"Missing '{cls.MULTITON_KEY_ATTR}' argument")
        # pick a raw key from dev.<attr>, raise if missing
        if not hasattr(dev, cls.MULTITON_KEY_ATTR):
            raise AttributeError(
                f"Object {dev!r} is missing required attribute '{cls.MULTITON_KEY_ATTR}'"
            )
        raw_key = getattr(dev, cls.MULTITON_KEY_ATTR)
        # ensure thread safe access to the registry
        with cls._lock:
            if raw_key in cls._instances:
                return cls._instances[raw_key]
            # otherwise build & cache a new one
            inst = super().__call__(*args, **kwargs)
            cls._instances[raw_key] = inst
            return inst
