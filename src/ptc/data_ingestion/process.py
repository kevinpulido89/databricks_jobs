"""
PTC DATA INGESTION process code.
"""
from libs.lola_utils.execution import Process as BaseProcess
from ptc.base import Base


class Process(BaseProcess):
    """_summary_

    Args:
        BaseProcess (_type_): _description_
    """

    def __init__(self):
        """
        Initializes the required variables.
        """
        super().__init__()
        self.b = Base()

    def validate_process(self):
        return True, "PTC DATA INGESTION process"

    def execute_process(self) -> None:
        """_summary_
        Raises:
            exc: _description_
        Returns:
            bool: _description_
        """
        print(">>> PTC Process: DATA INGESTION")
        self.b.mgs_secundario()

        return None


if __name__ == "__main__":
    Process().execute_process()
