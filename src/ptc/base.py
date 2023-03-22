"""
Module to define the base class for all PTC processes. Here it is where
the AML authentication is defined.
"""

from libs.lola_utils.config import CONFIG


class Base:
    """Define common functionality across various subprocess of smdc"""

    def __init__(self) -> None:
        """Initializes the required variables."""
        print("\n>>> PTC Base initialized:")
        self.mgs_importante()

    def mgs_importante(self) -> None:
        print("Hola Miguel Arquez")

    def mgs_secundario(self) -> None:
        print("Hola Doctor Quiroz")
