"""Class for managing scripts
"""

from ichigo.managers import Manager
from ichigo.scripting import ObservingSequence

class ScriptManager(Manager):
    """Executes TXT observing scripts.
    """
    def __init__(self) -> None:
        """Initializes the ScriptManager object.
        """
        super().__init__()
    
    def execute_obs_script(self, path: str) -> None:
        """Executes an observing script.

        Parameters
        ----------
        path: str
            Path to the script.
        
        Returns
        -------
        None
        """
        sequence = ObservingSequence(path, self.servers_dict)
        sequence.parse_script()
        sequence.execute_script()
    
    def execute_line(self, line: str) -> None:
        """Executes one line of an observing script.

        Parameters
        ----------
        line: str
            A line following the syntax as described in ObservingSequence.parse_line.

        Returns
        ------
        None
        """
        sequence = ObservingSequence("", self.servers_dict)
        # Directly parse a single line and execute the returned partial function
        result = sequence.parse_line(line)()
        if result is not None:
            print(f"Returned value: {repr(result)}")