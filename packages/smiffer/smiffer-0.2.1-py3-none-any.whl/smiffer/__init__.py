r"""Main function.

Linting
-------
```sh
    $ pylint src/smiffer/
```

Usage
-----
```sh
    # Execute this command line to test the module.
    $ smiffer -i data/input/1EHE.pdb \
                     -p data/input/1EHE_parameters.yml \
                     -a data/input/1EHE_APBS_output.dx \
                     -o data/output/

    # To display help on how to launch module.
    $ smiffer --help
```
"""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__version__ = "0.2.1"
__date__ = "15/10/2024"
__copyright__ = "MIT License"

# [D]
from datetime import datetime

# [T]
from time import time

# [G]
from .grid import grid

# [P]
from .parse_yaml import parse_yaml

# [U]
from .utils import parse_argument, WriteJson


def main():
    """Main function, used as an entry point for `pip`."""
    # Starting the timer to compute execution time.
    start_time: float = time()

    # Saving the starting launching time.
    begin_date: str = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    # Saving the starting launching time.
    date: str = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")

    argument = parse_argument(__version__)

    # YAML parsing.
    yaml = parse_yaml(argument.parameter, argument.verbose)
    yaml.clean()

    if argument.verbose:
        print(yaml)

    # Metadata linked to the arguments.
    argument_data: dict = {
        "input_file": argument.input,
        "output_directory": argument.output,
        "apbs_file": argument.apbs,
        "parameter_file": argument.parameter,
    }

    # Metadata linked to script time execution.
    timing_data: dict = {
        "script_version": __version__,
        "launch_time": begin_date,
        "end_time": datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
        "execution_time": f"{time() - start_time} seconds",
    }

    grid(yaml=yaml, argument=argument, date=date)

    # JSON writing.
    json: WriteJson = WriteJson(
        yaml_parser=yaml, argument=argument_data, timing=timing_data
    )

    if argument.verbose:
        print(json)

    json.write(path=argument.output, verbose=argument.verbose, date=date)
