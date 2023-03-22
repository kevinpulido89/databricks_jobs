"""
Create and interact with a singleton logger and log handlers.

Classes:

    LogManager(metaclass=Singleton)
        A class that manages logging and log handlers for a
        Service or Process
"""

import logging
from logging import StreamHandler, Formatter

import importlib

from libs.lola_utils.config import CONFIG
from libs.lola_utils.ind import Singleton
from libs.lola_utils.logging import TqdmToLogger


class LogManager(metaclass=Singleton):
    """
    A class that manages logging and log handlers for a
        Service or Process
    """
    @classmethod
    def get_logger(cls, name):
        """
        Creates Logger instance.

        Args:
            name(str): Name of the Logger object (usually file name).

        Returns:
            logging.logger: Logger instance.
        """
        # TODO: Once all LOLA code is running Python>=3.8, we can use basicConfig
        # with force=True. This is not supported in logging for Python 3.7 or below, so
        # we have to explicitly add handlers rather than using basicConfig, since basicConfig
        # will only take effect the first time it's called and will not change the root handler(s)
        # afterward, regardless of if the method is called with different parameters.

        fmt = CONFIG.logging.format
        level = CONFIG.logging.level
        handlers = cls.get_handlers()

        # Get root logger
        lgr = logging.getLogger(name=name)
        lgr.setLevel(level)

        # Clear handlers
        if (lgr.hasHandlers()):
            lgr.handlers.clear()

        # Set up formatting for handlers
        formatter = Formatter(fmt=fmt)
        for hndlr in handlers:
            hndlr.setFormatter(formatter)
            lgr.addHandler(hndlr)

        # Ensure that exactly one stream handler is returned

        # Get list of any standard streamhandlers
        str_handlers = [h for h in lgr.handlers if isinstance(h, logging.StreamHandler)
                        and not isinstance(h, logging.FileHandler)]
        # Get list of any root streamhandlers
        root_str_handlers = [h for h in lgr.root.handlers if isinstance(h, logging.StreamHandler)]

        # Remove any duplicate standard stream handlers - we are guaranteed at least one from get_handlers
        for hdlr in str_handlers[1:]:
            lgr.removeHandler(hdlr)

        # Remove any root stream handlers
        for hdlr in root_str_handlers:
            lgr.root.removeHandler(hdlr)

        return lgr

    @classmethod
    def get_tqdm_logger(cls, name):
        """
        Creates Tqdm Logger instance.
        Usage:ip
            tqdm_out = LM.get_tqdm_logger(__name__)
            for x in tqdm(range(100), file=tqdm_out):
                time.sleep(0.2)
        Args:
            name (str): Name of the Logger object (usually file name).

        Returns:
            logging.logger: Logger instance.
        """
        return TqdmToLogger(cls.get_logger(__name__))

    @classmethod
    def get_handlers(cls):
        """
        Create instances of handlers based on config supplied. StreamHandler is always present.
        Returns:
            list: List of handler instances
        """

        # Create handler instances. Intentionally not caching any errors here.
        # Force keep StreamHandler.
        handler_instances = [StreamHandler()]
        handler_strs = []
        try:
            handler_strs = CONFIG.logging.handlers.split(",")
        except AttributeError:
            pass
        handlers = importlib.import_module("libs.lola_utils.logging.handlers")
        for handler_str in handler_strs:
            _class = getattr(handlers, handler_str.strip())
            handler_instance = _class()
            handler_instances.append(handler_instance)

        cls.handlers = handler_instances
        return cls.handlers

    @classmethod
    def flush_all(cls, logger) -> int:
        """Method to flush logs

        Args:
            logger (logger object): logger being used
        Returns:
            count (int): Returns how many handlers were flushed
        """
        try:
            count = 0
            for hndlr in logger.handlers:
                hndlr.flush()
                count += 1
            return count
        except Exception:
            return count
