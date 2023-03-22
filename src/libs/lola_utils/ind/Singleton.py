"""
Use this module's Singleton class to enforce singleton-like behavior
on Python objects
"""

from abc import ABCMeta


class Singleton(ABCMeta):
    """
    In object-oriented programming , a singleton class is a class that can have only one object at a given point
    of time.

    Since Python inherently doesn't support Singletons, this class acts as a work around by keeping a list of
    active instances of a given class.

    Assign this class as meta for any class to make that class a singleton.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        When a given class is instantiated, we check if have an instance of that class already or not before
        creating a new instance.
        Args:
            *args (tuple): Arguments to the class call.
            **kwargs (dict): Keyword arguments to the class call.

        Returns:
            Object: An instance of the requested class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def destroy(cls):
        """
        Destroys an active instance of a given class.
        """
        if cls in cls._instances:
            del cls._instances[cls]
