"""
Contains the Process class for microservice execution
"""

import importlib
from typing import Tuple

from libs.lola_utils.logging import LogManager as LM


class Process:
    """
    Base process class.
    """
    logger = None

    def __init__(self):
        """
        Initialisation method of Process class.
        """
        self.logger = LM.get_logger(__name__)

    def execute_process(self) -> None:
        raise NotImplementedError("No execute_process() method implemented for this Process.")

    def validate_process(self) -> Tuple[bool, str]:
        msg = ("No validate_process() method implemented for this Process. Continuing with execution...")
        self.logger.info(msg)
        return (True, msg)

    @staticmethod
    def get_process_instance(service: str, process: str):
        """
        Creates instance of particular process.
        Args:
            service(str): Name string of the service.
            process(str): Name string of the process.
        Returns:
            process_instance(<service>.<process>): process_instance of the input process from the input service.
        """
        process = importlib.import_module(f"{service}.{process}")
        process_class = getattr(process, "Process")
        return process_class()
