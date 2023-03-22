"""
Placeholder module docstring
"""
import io
import logging


class TqdmToLogger(io.StringIO):
    """
        Output stream for TQDM which will output to logger module instead of
        the StdOut.
    """
    logger = None
    level = None
    buf = ''

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level

    def write(self, buf: str):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)
