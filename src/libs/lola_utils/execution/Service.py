"""
Contains the Service class for finding and handling Processes
"""
from abc import ABC
import os

from libs.lola_utils.ind import PathHelpers


class Service(ABC):
    """
    Service process class.
    """

    @staticmethod
    def get_all_services(root_path: str) -> [str]:
        """
        Fetches all the service names by traversing the directory file structure.
        Args:
            root_path(str): path to root directory
        Returns:
            list: list of all valid services.
        """
        services = PathHelpers.get_folders_having_filename(
            root_path, 'Service.py', True)

        # remove root dir if it is included
        root_dir = os.path.basename(os.path.normpath(root_path))
        if root_dir in services:
            services.remove(root_dir)
        return services

    @staticmethod
    def get_all_processes(root_path: str, service: str) -> [str]:
        """
        Fetches all the process names for the service name passed as parameter by traversing the directory
        file structure.
        Args:
            root_path(str): path to root directory
            service(str): pass the output service name
        Returns:
            list: list of all valid processes.
        """
        service = service.lower()
        folder_path = PathHelpers.get_full_file_name(root_path, service)
        process = list(map(lambda ls: ".".join(
            ls), PathHelpers.get_subfolders_having_filename(folder_path, 'Process.py', True)))
        return process

    @staticmethod
    def get_all_service_groups(root_path: str) -> dict:
        """
        Gets all valid services and their processes as a dict
        Args:
            root_path(str): path to root directory
        Returns:
            dict: dict containing all valid services with associated processes
        """
        group_dict = {}
        services = Service.get_all_services(root_path=root_path)

        for service in services:
            group_dict[service] = Service.get_all_processes(root_path=root_path, service=service)

        return group_dict
