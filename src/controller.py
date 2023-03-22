"""
This script named 'controller' is created to instantiate lola_utils Controller.
The command line arguments accepted by lola_utils Controller are passed to
'controller.py'.
Usage:
From terminal, use the following command:
python controller.py
    --service <service_name>
    --processes <comma separated process_names>
    --service_root_path <path to directory where services and processes exist>
    --service_config_path <name of json service(s) config file(s)>
                        for example: feature_store.json,default.json
"""
import logging
import os
import sys
from argparse import SUPPRESS, ArgumentParser
from typing import Any, Dict, List

from dotenv import load_dotenv

from libs.lola_utils.config import ConfigManager
from libs.lola_utils.execution import Controller
from libs.lola_utils.ind import PathHelpers


class ServiceInitializer:
    """
    This class is used to initialize services. Handles two main actions:
    catch the terminal arguments required by the controller and call the
    initializer method. It takes two arguments, a controller instance
    and a dictionary with additional arguments.
    The class initializes the controller, root path, service, processes
    arguments, configs files, args, sys.argv, and additional configs. It
    then calls the initializer() method to initialize the services.

    Parameters:
        controller_instance (Controller): An instance of the Controller
                                          class.
        additional_arguments (Dict[str, Any]): A dictionary of aditional
                                               arguments to load in the
                                               CONFIG. Defaults to None.
    Returns:
        None
    """

    def __init__(
        self,
        controller_instance: Controller,
        additional_arguments: Dict[str, Any] = None,
    ) -> None:
        self.controller = controller_instance
        self.rp = self.controller.root_path
        self.service = sys.argv[sys.argv.index("--service") + 1].split(",")
        self.processes_args = sys.argv[sys.argv.index("--processes") + 1].split(",")
        self.configs_files = sys.argv[sys.argv.index("--service_config_path") + 1].split(",")
        self.additional_arguments = additional_arguments

        self.initializer()

    def initializer(self) -> None:
        """
        This function is used to orchestrate the initialization of the
        service. It prints a message to the console to indicate that the
        service has been initialized. It then calls the config_builder()
        function to read in the configuration files and set the parameters.
        Finally, the controller.execute_processes() method is called to
        execute the processes. At the end, the logging system is shut down.

        About logging.shutdown method: When no argument is passed to it , the
        logging._handlerList is used as the default value for parameter
        handlerList in logging.shutdown method. Logging._handlerList is global
        and contains weak references to standard and custom log handlers.
        Weak references are created using the _addHandlerRef method in __init__
        method of Handler class in logging module. logging.shutdown() informs
        the logging system to perform an orderly shutdown by flushing and
        closing all handlers. This should be called at application exit and no
        further use of the logging system should be made after this call. Ref:
        https://docs.python.org/3/library/logging.html#logging.shutdown
        Args:
            None
        Returns:
            None
        Raises:
            Init_error: When there is an error during the config_builder
                        execution or during the controller.execute_processes()
        """

        print(f"\n🏁 {self.service[0]} Initialized...\n")

        try:
            # Additional configs can be passed in the command line argument 'service_config_path'
            # Multiple configs can be passed, separated by comma without blank spaces.
            self.config_builder(
                config_files=self.configs_files,
                additional_arguments=self.additional_arguments,
            )
            self.controller.execute_processes()
        except Exception as Init_error:
            logging.error(f"Invalid process {Init_error}")
            raise Init_error
        finally:
            print(">>> Shutting down logger")
            logging.shutdown()

    def config_builder(
        self, config_files: List[str], additional_arguments: Dict[str, Any] = None
    ) -> None:
        """
        This function is used to build the configuration for a controller.
        It takes as input the list of json config files and a dictionary
        of additional configurations. It then uses the ConfigManager to
        upsert the configuration from the files and additional configurations.
        If there is an error, it raises a Exception. From the rp
        (controller root path) + the path to main folder of config json
        files + the list of json config files + aditional arguments creates
        the CONFIG class which will be used during the service execution

        Args:
            config_files (List[str]): list of names of the  json files
                                      involved in the services
            additional_arguments (Dict[str, Any], optional): A dictionary of
                                               aditional arguments to load in
                                               the CONFIG. Defaults to None.
        Returns:
            None

        Example:
            config_builder(config_files=['feature_store.json', 'default.json'],
                           additional_arguments={'param1': 'value1', 'param2': 'value2'})
        """
        try:
            CONFIG_PATH = os.path.join(os.getenv("CONFIG_DIR"), os.getenv("COUNTRY"))
            for _config_file in config_files:
                config = PathHelpers.get_full_file_name(self.rp, f"{CONFIG_PATH}/{_config_file}")
                ConfigManager().upsert_config_from_file(config)

            if additional_arguments:
                ConfigManager().upsert_config(additional_arguments)

        except Exception as e:
            print(f"ConfigurationError: {e}")
            raise e


if __name__ == "__main__":
    # load environment variables from the .env file.
    load_dotenv()

    # Parse production configs
    _parser = ArgumentParser()
    _parser.add_argument("--FEATURES_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--TRAIN_MODEL", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--MODEL_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--CREATE_RECOMMENDATIONS", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--DEMAND_CURVES_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--ZTPM_PRICES_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--BOUNDARIES_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--OPT_OUTPUT_PATH_ID", type=str, default="", help=SUPPRESS)
    _parser.add_argument("--mode", type=str, default="train", help="train (default) or predict")

    args, sys.argv = _parser.parse_known_args()
    sys.argv = ["controller.py"] + sys.argv
    _additional_arguments = vars(args)

    # instantiate the Controller class
    _controller = Controller()

    # Call the Service Initializer class to trigger
    ServiceInitializer(controller_instance=_controller, additional_arguments=_additional_arguments)
