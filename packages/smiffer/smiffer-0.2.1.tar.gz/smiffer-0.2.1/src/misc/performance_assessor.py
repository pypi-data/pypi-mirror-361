r"""Launch this script in order to test the program's performance.

Usage
-----
```sh
    # Execute this command line in a conda environment.
    $ python -m src.smiffer.performance_profile
```
"""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


# [D]
from dataclasses import dataclass

# [O]
from os import makedirs

# [S]
from shutil import rmtree

# [P]
from perfassess.class_performance_assessor import PerformanceAssessor

# [G]
from smiffer.grid.grid import grid

# [P]
from smiffer.parse_yaml.parse_yaml import parse_yaml


@dataclass
class ArgumentParser:
    """To simulate parsed arguments"""

    def __init__(self, pdb_input: str, output: str, parameter: str, apbs: str):
        """Initiate a ArgumentParser dataclass object.

        Parameters
        ----------
        pdb_input : `str`
            Input PDB.

        output : `str`
            Output directory.

        parameter : `str`
            YAML parameters file.

        apbs : `str`
            APBS file.
        """
        self.input: str = pdb_input
        self.output: str = output
        self.parameter: str = parameter
        self.apbs: str = apbs
        self.verbose: bool = False


def to_test(
    pdb_input: str,
    output: str,
    parameter: str,
    apbs: str,
):
    """The function to launch in order to test the program efficiency.

    Parameters
    ----------
    pdb_input : `str`
        The PDB to input.

    output : `str`
        The PDB to output.

    parameter : `str`
        The YAML parameter to test.

    apbs : `str`
        The APBS file to use.
    """
    argument = ArgumentParser(pdb_input, output, parameter, apbs)

    # YAML parsing.
    yaml = parse_yaml(argument.parameter, argument.verbose)
    yaml.clean()

    grid(yaml=yaml, argument=argument, date="0000_00_00")


if __name__ == "__main__":
    __YAML: dict = {
        "pdb_input": "data/6X3V.pdb",
        "output": "data/.tmp",
        "parameter": "data/6X3V_parameter.yml",
        "apbs": "data/6X3V_APBS.dx",
    }

    makedirs(__YAML["output"], exist_ok=True)
    assessor: PerformanceAssessor = PerformanceAssessor(
        main=to_test, n_field=1, **__YAML
    )

    assessor.launch_profiling()
    assessor.plot(path="docs/ressources/plot/")

    rmtree(__YAML["output"])
