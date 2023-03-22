"""
Write logs to a file.
"""

import logging

from libs.lola_utils.config import CONFIG
from libs.lola_utils.ind import Singleton


class FileHandler(logging.FileHandler, metaclass=Singleton):
    """
    Class that logs to a file.
    Inherits from python logging module (FileHandler)
    """
    logName = None

    def __init__(self):
        """
            Create instance of File Handler based on config supplied.

            config:
                filename

            Returns:
                object: File handler object

        """
        self.logName = CONFIG.logging.filename
        super().__init__(self.logName)
