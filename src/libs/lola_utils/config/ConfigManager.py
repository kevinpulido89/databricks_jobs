"""
This module provides a convenient object with which to store and update configs. Functions are
implemented using python_json_config's ConfigBuilder. The ConfigManager class is implemented
as a Singleton to provide easy access to configs from other utils.

Classes:

    ConfigManager(metaclass=Singleton)
        A class that stores and manages configurations for services or processes.

"""

import json
import logging
import os

from python_json_config import ConfigBuilder
from python_json_config.config_node import ConfigNode, Config
from python_json_config.utils import normalize_path
from typing import Any, List, Union

from libs.lola_utils.ind import Singleton, PathHelpers


class ConfigManager(metaclass=Singleton):
    """
    ConfigManager
    A class that stores and manages configurations for services or processes.
    """

    config = None

    def __init__(self):
        """
            Method to instantiate default Config Manager.
            All service-specific configs should be added as environment variables, or passed
            in using the below methods as a path to a json file or a dict object.
        """
        default_logging_config = {
         "logging": {
            "level": "INFO",
            "format": "%(asctime)s:%(levelname)s:%(process)d:%(name)s:%(module)s:%(lineno)d:%(message)s"
            }
        }
        builder = ConfigBuilder()
        builder.set_field_access_required()
        self.config = builder.parse_config(default_logging_config)
        self.__set_method_get_value_or_none()
        self.append_env_config(key_prefix="config_")

    def __set_method_get_value_or_none(self) -> None:
        """Method to set get_value_or_none as an object method in config object.
        Returns:
            None
        """

        def set_strict_access(config_node: Union[Config, ConfigNode],
                              key_path: Union[str, List[str]], access_value: bool) -> str:
            """Set value of strict_access attribute of config_node and it's valid child config_nodes,
            to the value received in argument access_value.
            set_strict_access method returns the key path (containing dot separated keys)
            for which strict_access value has been set.
            The same key path can be passed to set_strict_access method to reset the values
            of set strict_access attributes.
            Args:
                config_node (Union[python_json_config.config_node.Config,
                python_json_config.config_node.ConfigNode]): Config node object for which value of strict_access is set.
                key_path (Union[str, List[str]]): Key path,
                                                  either a string containing dot separated keys or a list of keys.
                access_value (bool): Boolean value, True or False, which is set as value of attribute strict_access.
            Returns:
                str: string key path containing dot separated keys for which attribute strict_access has been set.
            """
            config_node.strict_access = access_value
            if key_path:
                # normalize_path returns a list containing individual keys present in key_path.
                # Input to normalize_path can be either 'key1.key2' or ['key1', 'key2']
                # Return value of normalize_path method is ['key1', 'key2'].
                key_path_sub_strings = normalize_path(key_path)
                value = config_node.get(key_path_sub_strings[0])
                if isinstance(value, ConfigNode):
                    return set_strict_access(value, key_path_sub_strings[1:], access_value)
            return config_node._ConfigNode__path_str

        def get_value_or_none(key_path: Union[str, List[str]]) -> Any:
            """Retrieve value of a config, present with the given key path. If the key does not exist, None is returned.

            To get value of a config key while ignoring when missing,
            this method needs to be called as an object method of Config object.
            Example Usage: CONFIG.get_value_or_none("DateDict.SCHEMA.COLUMNS.YEAR.NAME")
            CONFIG.DateDict.SCHEMA.COLUMNS.YEAR.NAME always refers to get method of
            python_json_config.config_node.ConfigNode class.

            The third party module 'python_json_config.config_node' does not support
            contextual setting of strict_access attribute.
            Attributes strict_access, required_fields and optional_fields are set by the ConfigBuilder object
            before creating Config object and it's ConfigNodes.
            Hence, this method sets strict_access attribute of parent config nodes of the referenced key to False.
            This enables get method of ConfigNode/Config object to return None when the key is missing.
            After retrieving the value of referenced key,
            strict_access attribute of it's parent config nodes are set to True.
            Args:
                key_path (Union[str, List[str]]): Key path,
                                                  either a string containing dot separated keys or a list of keys.
            Returns:
                Any: Value of the referenced key.
            """
            latest_config_node_path_str = set_strict_access(self.config, key_path, False)
            value_or_excep = self.config.get(key_path)
            set_strict_access(self.config, latest_config_node_path_str, True)
            return value_or_excep

        self.config.get_value_or_none = get_value_or_none

    def replace_config_from_file(self, config_file_path: str):
        """
        Method to update and replace in the main config from a json file. If a key's value in the main
        config is a nested dict, that whole value is replaced by the incoming value (whether a dict or
        a value of some other type). This allows nested groups of configs to be replaced easily.
        Args:
            config_file_path (str) : Path to config file source.
        Returns:
            None
        """

        if PathHelpers.check_file_existence(config_file_path):
            self.__replace_config_from_file(config_file_path=config_file_path)
        else:
            raise FileNotFoundError(f"{config_file_path} file doesn't exist")

    def upsert_config_from_file(self, config_file_path: str):
        """
        Method to update and append (upsert) to the main config from a json file.
        When individual keys are matched between the main config and the new file, the value is updated.
        New key/value pairs are appended to the main config.
        Args:
            config_file_path (str) : Path to config file source.
        Returns:
            None
        """

        if PathHelpers.check_file_existence(config_file_path):
            self.__upsert_config_from_file(config_file_path=config_file_path)
        else:
            raise FileNotFoundError(f"{config_file_path} file doesn't exist")

    def replace_config(self, new_config: dict):
        """
            Method to add runtime configs.
        Args:
            new_config (dict) : Config to add.
        Returns:
            ConfigManager : The ConfigManager for chaining of calls.
        """
        if type(new_config) is not dict:
            raise ValueError(
                f"Expected dict value for new_config but got {type(new_config)}")

        self.__replace_config(new_config=new_config)
        return self

    def upsert_config(self, new_config: dict):
        """
            Method to add runtime configs.
        Args:
            new_config (dict) : Config to add.
        Returns:
            ConfigManager : The ConfigManager for chaining of calls.
        """
        if type(new_config) is not dict:
            raise ValueError(
                f"Expected dict value for new_config but got {type(new_config)}")

        self.__upsert_config(new_config=new_config)
        return self

    def append_env_config(self, key_prefix: str, subdict_specifier: str = '__'):
        """
            Update config with env variables. The env variables should be set using the dot operator.
            For example: config.logging.level
            Note: Most OS allows only strings to be set as env variables. Be aware of that. If this is a
            concern we can do some crazy type manipulation here. But let's avoid it until it is absolutely
            necessary.
            Note: This method is automatically called for you via controller. You shouldn't need to call this
            method manually ever.
        Args:
            key_prefix(str) : prefix for matching on specific keys that should be added to the config
            from environment variables.
            subdict_specifier: string specifier that denotes a desired subdict split. For example, with an env
            variable of 'config_logging__testkey', calling append_env_config(key_prefix='config_',
            subdict_specifier='__') would result in the addition of 'logging.testkey' to the config dict.
        Returns:
            None
        """
        for key in os.environ:
            # TODO: this needs to be fixed for windows. works fine on linux. as updating os.environ will not update
            # TODO: the system environment in windows
            if key.startswith(key_prefix):
                self.config.add(key.replace(key_prefix, '', 1).replace(subdict_specifier, '.'), os.environ[key])

    def __get_recursive_key_paths_values(self, d: dict, path_prefix=''):
        """
            Method to get dotted path string of all keys and corresponding values in a nested dictionary.
        Args:
            d(dict): Input dictionary for which the key paths and values need to be returned.
            path_prefix(str): Optional string containing parent key name with dot.
        Returns:
            tuple: Tuple containing dotted path string of key and its value.
        """
        for key, value in d.items():
            if type(value) is dict:
                yield from self.__get_recursive_key_paths_values(d=value, path_prefix=path_prefix + key + '.')
            else:
                yield path_prefix + key, value

    @staticmethod
    def read_config_from_file(config_file_path: str) -> dict:
        """
        Static method to read a config from config file into a dict.
        Args:
            config_file_path(str) : Path of the config file to be read.
        Returns:
            dict: Json content of the file.
        """
        with open(config_file_path) as f:
            json_values = json.load(f)

        return json_values

    def __replace_config_from_file(self, config_file_path: str) -> None:
        """
        Update/replace operation on the config from a given config file path.
        If a key matches between the main config and the incoming config, and the value is a nested dict,
        the entire nested dict in the main config is replaced with the incoming dict. If the keys match
        and the incoming value is not a dict, the value is simply updated. Any new keys from the incoming
        dict are automatically appended.
        Args:
            config_file_path(str) : Path of the config file to be read.
        Returns:
            None
        """
        new_config = ConfigManager.read_config_from_file(config_file_path=config_file_path)
        self.__replace_config(new_config=new_config)

    def __replace_config(self, new_config: dict) -> None:
        """
        Update/replace operation on the config from an incoming config dict.
        If a key matches between the main config and the incoming config, and the value is a nested dict,
        the entire nested dict in the main config is replaced with the incoming dict. If the keys match
        and the incoming value is not a dict, the value is simply updated. Any new keys from the incoming
        dict are automatically appended.
        Args:
            new_config(dict) : New config dict to be used as a source for the update/replace operation.
        Returns:
            None
        """
        existing_keys = self.config.to_dict().keys()
        for key, value in new_config.items():
            if type(value) is dict and (key in existing_keys):
                for k, v in value.items():
                    self.config.get(key).update(k, v)
            else:
                self.config.update(key, value, True)

    def __upsert_config_from_file(self, config_file_path: str) -> None:
        """
        Upsert operation on the config from a given config file path.
        This method accomplishes a straight upsert from the incoming config dict to the main config. Any matching keys
        trigger an update regardless of value type, and any new keys are appended to the main config.
        Args:
            config_file_path(str) : Path of the config file to be read.
        Returns:
            None
        """
        new_config = ConfigManager.read_config_from_file(config_file_path=config_file_path)
        self.__upsert_config(new_config=new_config)

    def __upsert_config(self, new_config: dict) -> None:
        """
        Upsert operation on the config from a given config dict.
        This method accomplishes a straight upsert from the incoming config dict to the main config. Any matching keys
        trigger an update regardless of value type, and any new keys are appended to the main config.
        Args:
            new_config(dict) : New config dict to be used as a source for the upsert operation.
        Returns:
            None
        """
        for key, value in self.__get_recursive_key_paths_values(d=new_config):
            self.config.update(key, value, True)
