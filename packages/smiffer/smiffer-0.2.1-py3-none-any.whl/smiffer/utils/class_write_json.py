"""Contains a class in order to write a ".json" metadata file."""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


# [S]
from sys import version

# [J]
from json import dumps


class WriteJson:
    """Write a ".json" file with metadata.

    Attributes
    ----------
    self.__json : `dict`
        The grid on which to apply gaussian.
    """

    def __init__(self, yaml_parser: object, argument: dict, timing: dict):
        """Initialize a dictionary that will be written as a ".json" file.

        Parameters
        ----------
        yaml_parser : `ParseYaml`
            A ParseYaml object already instantiated.

        argument : `dict`
            A dictionary with metadata linked to input arguments.

        timing : `dict`
            A dictionary with metadata linked to script time execution.
        """
        # Get all attributes from the yaml_parser.
        self.__json: dict = dict(yaml_parser.items())

        # Given arguments.
        self.__json["given_argument"] = argument

        # Add other metadata.
        self.__json["other"] = timing
        self.__json["other"]["python_version"] = version

    def write(self, path: str, date: str, verbose: bool = False):
        """Write the ".json".

        Parameters
        ----------
        path : `str`
            The path to write the ".json" file.

        date : `str`
            The launching time.

        verbose : `bool`, optional
            Use verbose mode or not. By default, set to `False`, so verbose
            mode is disabled.
        """
        path = f"{path.rstrip('/')}/{date}_metadata.json"

        with open(path, "w", encoding="utf-8") as file:
            file.write(dumps(self.__json, indent=4))

        if verbose:
            print(f'> Metadata file written as "{path}".')

    def __str__(self) -> str:
        """Redefine the `print()` function behaviour in order to enhance
        the object print readability.

        Returns
        -------
        `str`
            The new message to print.
        """
        to_print: str = "\033[7m CURRENTS METADATA TO SAVE \033[0m\n"

        for key, value in self.__json.items():
            # Print, if there is, sub-dictionary.
            if isinstance(value, dict):
                to_print += f"- {key}:\n"

                for sub_key, sub_value in value.items():
                    to_print += (
                        f"{' ' * 4}- {sub_key}: \033[2m{sub_value}" "\033[0m\n"
                    )
            else:
                # Print the key normally and the value in light grey.
                to_print += f"- {key}: \033[2m{value}\033[0m\n"

        return to_print[:-1]
