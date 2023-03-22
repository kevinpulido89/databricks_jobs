"""
Contains the functionality to aid in finding the path of modules, files, or directories.
"""
import os
import pathlib
from pathlib import Path
import shutil

import rootpath


class PathHelpers:
    """
    This class will help in finding the path of module, file or directory.
    """

    @staticmethod
    def create_directory_if_not_exist(relative_path: str) -> str:
        """
        Create directories if not present. This supports recursive directory creation.
        Args:
            relative_path (str): Relative path to root of the project.
        Returns:
            str: Absolute path of the directory.
        """
        # Remove last slash as it is redundant.
        if relative_path[-1] == "/":
            relative_path = relative_path[:-1]
        if not os.path.exists(PathHelpers.get_full_path_name(relative_path)):
            # Relative path and recursive request.
            if (relative_path[0] != "/") and ("/" in relative_path):
                paths = relative_path.split("/")
                path = "/".join(paths[:-1])
                if not os.path.exists(PathHelpers.get_full_path_name(path)):
                    PathHelpers.create_directory_if_not_exist(path)
            os.mkdir(PathHelpers.get_full_path_name(relative_path))
        return PathHelpers.get_full_path_name(relative_path)

    @staticmethod
    def delete_directory_if_exists(relative_path: str) -> bool:
        """
        Delete directories if present.
        Args:
            relative_path (str): Relative path to root of the project.
        Returns:
            bool: True if the file is Deleted/Doesn't exist, else False
        """
        if os.path.exists(PathHelpers.get_full_path_name(relative_path)):
            shutil.rmtree(PathHelpers.get_full_path_name(relative_path))
        return not os.path.isdir(relative_path)

    @staticmethod
    def delete_file_if_exists(relative_path: str) -> None:
        """
        Delete file if present.
        Args:
            relative_path (str): Relative path to root of the project.
        Returns:
            None
        """
        if os.path.exists(PathHelpers.get_full_path_from_root(relative_path)):
            os.remove(PathHelpers.get_full_path_from_root(relative_path))

    @staticmethod
    def get_output_dir_path(folder_name: str) -> str:
        """
        Returns the path of the folder where output files are stored.
        Args:
            folder_name (str): pass the output folder name.
        Returns:
            str: path where the results are getting stored.
        """
        return os.path.join(os.path.abspath(os.path.join(os.getcwd(), os.pardir)), folder_name)

    @staticmethod
    def get_all_files_in_dir(dir_path: str, ext=None) -> [str]:
        """
        Returns a list of files with specified extension in a given directory.
        If ext is None, it will return all the files in a given directory.
        Args:
            dir_path (str): Path of the specified directory.
            ext (str): Return files only with this extension.

        Returns:
            list: List of files.
        """
        files = []
        # For the below variables, r is root, d is directories, f is files
        for r, d, f in os.walk(dir_path):
            for file in f:
                if ext:
                    if file.endswith(ext):
                        files.append(os.path.join(r, file))
                else:
                    files.append(os.path.join(r, file))
        return files

    @staticmethod
    def get_full_path_name(relative_path: str) -> str:
        """
        Get absolute path for a given relative path to the root of the project.
        Args:
            relative_path (str): Relative path to root of the project.

        Returns:
            str: Absolute path.
        """
        working_dir = os.path.abspath(os.getcwd())
        return os.path.join(working_dir, relative_path)

    @staticmethod
    def get_full_file_name(relative_path: str, filename: str) -> str:
        """
        Get absolute path for a given relative path and a filename to the root of the project.
        Args:
            relative_path (str): Relative path to root of the project.
            filename (str) : Name of the file

        Returns:
            str: Absolute path.
        """
        return os.path.join(PathHelpers.get_full_path_name(relative_path), filename)

    @staticmethod
    def get_working_directory() -> str:
        """
        Get the parent directory.

        Returns:
            str: Parent Folder name.
        """
        working_dir = os.path.basename(os.getcwd())
        return working_dir

    @staticmethod
    def check_file_existence(file: str) -> bool:
        """
            Checks if the file exists or not.
        Args:
            file (str): file_name
        Returns:
            bool : True if File exists else False.
        """
        return os.path.isfile(file)

    @staticmethod
    def is_empty_file(file: str) -> bool:
        """
        Checks if the File is Empty or Not.
        Args:
            file (str): file name with full path.
        Returns:
            bool : True if File is empty else False.
        """
        return os.stat(file).st_size == 0

    @staticmethod
    def get_root_path(file: str) -> str:
        """
            Gets the rootpath of the working directory
        Args:
            file (str): filename

        Returns:
            str: Root path of the folder
        """
        return rootpath.detect(file)

    @staticmethod
    def get_root_dir_name(file: str) -> str:
        """
            Gets the root folder name
        Args:
            file (str): filename

        Returns:
            str: Root folder name
        """
        return pathlib.PurePath(rootpath.detect(file)).name

    @staticmethod
    def get_folders_having_filename(dir_path: str, file_name: str, case_insensitive: bool = False) -> [str]:
        """
        Returns a list of subfolders within dir_path that contains the file_name.
        Args:
            dir_path (str): Path of the specified directory.
            file_name (str): Filename to be searched
            case_insensitive (bool): Should the search be case-sensitive or in-sensitive?

        Returns:
            list: List of folders.
        """
        folders = []
        directories = (entry for entry in os.scandir(dir_path) if entry.is_dir())
        for directory in directories:
            if case_insensitive:
                if len(list(entry for entry in os.scandir(directory.path)
                            if entry.name.lower() == file_name.lower())):
                    folders.append(directory.name)
            else:
                if len(list(entry for entry in os.scandir(directory.path) if entry.name == file_name)):
                    folders.append(directory.name)
        return folders

    @staticmethod
    def get_subfolders_having_filename(dir_path: str, file_name: str, case_insensitive: bool = False) -> [[str]]:
        """
        Returns a list of a set of folders that contains the file_name.
        Args:
            dir_path (str): Path of the specified directory.
            file_name (str): Filename to be searched
            case_insensitive (bool): Should the search be case-sensitive or in-sensitive?

        Returns:
            list: List of a list of subfolders.
        """
        folders: list = []
        base_path_set: tuple = Path(dir_path).parts
        # For the below variables, r is root, d is directories, f is files
        for r, d, f in os.walk(dir_path):
            for file in f:
                if case_insensitive:
                    check = file.lower() == file_name.lower()
                else:
                    check = file == file_name
                if check:
                    r_parts: tuple = Path(r).parts
                    folders.append([part for part in r_parts if part not in base_path_set])
        return folders

    @staticmethod
    def get_full_path_from_root(relative_path: str) -> str:
        """
            Gets the actual path of the given relative path
        Args:
            relative_path (str): relative path from the main directory
        Returns:
            str: actual path of the folder
        """
        return os.path.join(PathHelpers.get_root_path(__file__), relative_path)
