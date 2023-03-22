"""
_summary_
"""
# Importing global packages
from typing import Tuple

# Importing LOLA modules
from libs.lola_utils.config import CONFIG
from libs.lola_utils.execution import Process as BaseProcess

# Importing local modules
from ptc.base import Base


class Process(BaseProcess, Base):
    """_summary_

    Args:
        BaseProcess (_type_): Lola base process definition

    Raises:
        exc: _description_

    Returns:
        _type_: _description_
    """

    def __init__(self) -> None:
        super().__init__()

    def validate_process(self) -> Tuple[bool, str]:
        return True, "PTC FEATURE ENGINEERING process"

    def execute_process(self) -> None:
        """_summary_"""
        print(">>> PTC Process: FEATURE ENGINEERING")
        print(f"Estado del proceso: {CONFIG.state}")
        self.despedida()

    def despedida(self) -> None:
        print(f"Adios {CONFIG.username}")


if __name__ == "__main__":
    Process().execute_process()
