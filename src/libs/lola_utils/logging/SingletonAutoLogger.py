"""
Define a class with both Singleton and Autologger.
"""

from libs.lola_utils.ind import Singleton
from libs.lola_utils.logging import AutoLogger


class SingletonAutoLogger(Singleton, AutoLogger):
    """
    Class that inherits both Singleton and AutoLogger.
    To use, just mark this class as metaclass of the target class.
    """
    pass
