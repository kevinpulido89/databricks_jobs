"""
Discover, validate and execute Services and Processes.
"""

import argparse
import cProfile
import json
import logging
import os
import pstats

from libs.lola_utils.config import ConfigManager
from libs.lola_utils.execution import Process as BaseProcess
from libs.lola_utils.execution import Service as BaseService
from libs.lola_utils.ind import PathHelpers, Singleton


class Controller(metaclass=Singleton):
    """
    This class is used to create a single entry point for a Process or set of Processes. It functions
    in coordination with Process and Service classes to configure and control execution.
    """
    # Create parser and logger objects.
    parser = None
    logger = None
    root_path = None

    def __init__(self):
        """
        Initializes parser and logger objects. Sets the structure of arguments passed from command line.
        Args:
            None
        """
        self.parser = argparse.ArgumentParser()
        self.__set_arg_structure()
        self.root_path = self.get_args().service_root_path

    def perform_validation(self, service: str, process_list: list) -> bool:
        """
        This function validates the service or process by checking if it is present in the list of valid services
        or processes.
        Args:
            service (str): Name of service
            process_list ([str]): Name of process
        Returns:
             bool: True if valid, False if invalid
        """
        # Validate service.
        valid_service_list = BaseService.get_all_services(root_path=self.root_path)
        service = service.lower()

        # Deal with potential path to pip package
        if '/' in service:
            service = service[service.rindex('/')+1:].lower()

        # Deal with potential fully qualified service name
        if '.' in service:
            service = service[service.rindex('.')+1:].lower()

        if service in valid_service_list:
            # Validate process.
            valid_process_list = BaseService.get_all_processes(root_path=self.root_path, service=service)

            for process in process_list:
                if process.lower() not in valid_process_list:
                    logging.error(f"Invalid process name {process}")
                    return False
            return True

        else:
            logging.error(f"Invalid service name {service}")
            return False

    def get_args(self) -> argparse.Namespace:
        """
        Parses arguments
        Returns:
            parser.parse_args(): Returns this method that helps in parsing an argument.
        """
        return self.parser.parse_args()

    def __set_arg_structure(self) -> argparse.ArgumentParser:
        """
        The service, process, service_root_path, service_config_path and dm_config_path
        elements are added as arguments to parser.
        Returns:
            ArgumentParser: Parser object with arguments added.
        """
        self.parser.add_argument('--service', required=True, type=str, help='Please specify the service to run. ')
        self.parser.add_argument('--processes', required=True, type=str, help='Please specify the process names. ')
        self.parser.add_argument('--service_root_path', required=True, type=str,
                                 help='Please specify the service root path.')
        self.parser.add_argument('--service_run_id', required=False, type=str,
                                 help='Specify a unique identifier for this run of the specified service.')
        self.parser.add_argument('--service_config_path', required=False, type=str,
                                 help='Please specify the path to the service config file. Defaults to '
                                      + '<service root>/configs/services/<service>.json'
                                 )
        self.parser.add_argument('--dm_config_path', required=False, type=str,
                                 help='Please specify the path to the service config file. Defaults to '
                                      + '<service root>/configs/DataModels.json'
                                 )
        self.parser.add_argument('--locale', required=False, type=str,
                                 help='Please specify the locale to be used.')
        self.parser.add_argument('--language', required=False, type=str, help='Please specify the language.')
        self.parser.add_argument('--additional_configuration', required=False, type=str,
                                 help='Add any additional configuration values as a valid JSON string.')
        self.parser.add_argument('--profile', required=False, type=bool,
                                 help='Whether to profile the invocation of the process.')
        return self.parser

    def execute_processes(self) -> None:
        """
        Executes all the processes passed for service by instantiating their respective
        classes and calling their execute_process() methods.
        Returns:
            None
        """

        # Get arguments.
        service = self.get_args().service
        processes = self.get_args().processes.split(',')
        processes = [x.strip(' ') for x in processes]
        service_root_path = self.get_args().service_root_path
        service_config_path = self.get_args().service_config_path
        service_config_paths = None
        if service_config_path is not None:
            service_config_path = service_config_path.split(',')
            service_config_paths = [x.strip(' ') for x in service_config_path]
        service_run_id = self.get_args().service_run_id
        dm_config_path = self.get_args().dm_config_path
        locale = self.get_args().locale
        language = self.get_args().language
        additional_configuration = self.get_args().additional_configuration
        profile = self.get_args().profile

        # Check if service and data model configs were included as arguments.
        if service_config_path is None:
            service_config_path = os.path.join(self.root_path, 'configs', 'services', f"{service}.json")
        if dm_config_path is None:
            dm_config_path = os.path.join(self.root_path, 'configs', 'DataModels.json')
        if service_run_id is not None:
            ConfigManager().upsert_config({"service_run_id": service_run_id})
        if language is not None:
            language = language.lower()
            ConfigManager().upsert_config({"language": language})
        if locale is not None:
            locale = locale.lower()
            ConfigManager().upsert_config({"locale": locale})
        ConfigManager().upsert_config({"service": service})
        ConfigManager().upsert_config({"processes": processes})
        ConfigManager().upsert_config({"service_root_path": service_root_path})
        ConfigManager().upsert_config({"service_config_path": service_config_path})
        ConfigManager().upsert_config({"dm_config_path": dm_config_path})

        if self.perform_validation(service=service, process_list=processes):

            # Attempt to find and load config files. Log warning if file does not exist.
            if service_config_paths is not None:
                for p in service_config_paths:
                    if PathHelpers.check_file_existence(p):
                        ConfigManager().upsert_config_from_file(config_file_path=p)
                    else:
                        logging.warning(f"Warning: Service config file at {p} not found.")

            if PathHelpers.check_file_existence(dm_config_path):
                ConfigManager().upsert_config_from_file(config_file_path=dm_config_path)
            else:
                logging.warning("Warning: Data model config file not found or not provided.")

            # Load from environment variables with config prefix
            ConfigManager().append_env_config(key_prefix="config_")

            # Add additional configuration from JSON to ConfigManager
            if additional_configuration is not None:
                cfg = json.loads(additional_configuration)
                ConfigManager().upsert_config(cfg)

            for process in processes:
                # Validate process if validation method exists
                process_class = BaseProcess.get_process_instance(service, process)
                (valid, msg) = process_class.validate_process()
                if valid:
                    logging.info(f"Process {process} validated successfully. Executing...")
                    if profile:
                        filename = f'{process}_profile_stats'
                        logging.info(f"Profile results written to binary file {filename}.")
                        cProfile.runctx(statement='process_class.execute_process()', globals={}, locals={"process_class": process_class}, filename=filename)
                        stats = pstats.Stats(filename)
                        stats.print_stats(service)
                    else:
                        process_class.execute_process()
                    logging.info(f"Process {process} executed successfully.")
                else:
                    raise Exception(f"Error: Process {process} failed validation for the following reasons: {msg}")
        else:
            raise Exception("Invalid values passed to controller.")

    def get_parser(self) -> argparse.ArgumentParser:
        """
            Method to get the parser object.
        Returns:
            parser (argparse.ArgumentParser): Parser object created in this class.
        """
        return self.parser
