"""
Auto-log information about class methods and execution.
"""

import inspect
import logging
import time

from libs.lola_utils.config import CONFIG
from libs.lola_utils.logging import LogManager


class AutoLogger(type):
    """
        Class to auto-log information about start, end and runtime of all methods in a class.
        To use, just mark this class as metaclass of the target class.
    """

    def __new__(cls, name, bases, namespace):
        if logging.getLevelName(CONFIG.logging.level) <= logging.INFO:
            # We do this only in info or lower mode.
            logger = LogManager().get_logger(namespace["__module__"])
            namespace = {
                k: v if (k.startswith('__') or not inspect.isfunction(v)) else cls.calculate_execution_time(
                    name, v, logger
                )
                for k, v in namespace.items()}

            return type.__new__(cls, name, bases, namespace)

    @classmethod
    def calculate_execution_time(cls, module_name, function, logger):
        """
            This method adds the functionality of calculating the execution time of a function.
        Args:
            module_name(str): Name of the module in which the function is executed
            function(types.function): function for which execution time needs to be calculated.
            logger(logging.logger): logger instance

        Returns:
            Returns same as return statement of function.
        """
        def decorator(*args, **kwargs):
            """
                Function decorator
            """
            d = {"function_name": function.__name__, "module_name": module_name, "file_name": f"{module_name}.py"}
            start_time = time.time()
            logger.info(f'Start of execution of method: {function}', extra=d)
            try:
                result = function(*args, **kwargs)
            except TypeError as e:
                logger.error(f"TypeError: {e}")
                result = function.__func__()
                raise e
            except Exception as e:
                raise e
            logger.info(f'End of execution of method: {function}', extra=d)
            end_time = time.time()
            total_execution_time = end_time - start_time
            d["exec_time"] = total_execution_time
            logger.info(f'Total method execution time: {str(total_execution_time)}', extra=d)
            return result

        return decorator
