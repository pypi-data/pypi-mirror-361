"""Contains a class in order to parse a `.yaml` parameter file."""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [C]
from copy import deepcopy

# [Y]
from yaml import safe_load, dump

# [S]
from .class_set_parameter import SetParameter


class ParseYaml:
    """Parse a ".yml" file, set default values if needs to, and check given
    values.

    Attributes
    ---------
    self.__key : `list`
        A list of key to access parameters.

    self.__value : `list`
        Value linked to parameters.

    self.__category : `dict`
        A dictionary used to print parameters names and values link to a
        category name used as a key.

    self.__yaml : `dict`
        The parsed YAML file.

    self.__clean_yaml : `dict`
        A deep copy of the parsed YAML file, which deletion are applied on.
    """

    def __init__(self, file_path: str, verbose: bool = False):
        """Initialize attributes contained parsed ".yaml" file values.

        Parameters
        ----------
        file_path : `str`
            The path to the file to be parsed.

        verbose : `bool`, optional
            Use a verbose mode indicating when default values are used, by
            default `False` so do not print anything else.
        """
        # Initialize attributes.
        self.__key: list = []
        self.__value: list = []
        self.__category: dict = {}

        self.__verbose: bool = verbose
        self.__yaml: dict = {}

        if file_path is not None:
            # Parsing user file.
            with open(file_path, "r", encoding="utf-8") as file:
                self.__yaml: dict = safe_load(file)

        if self.__verbose:
            if self.__yaml == {}:
                print("> No parameter file given, switch to default values.")
            else:
                print(f'> "{file_path}" parameter file is parsed successfully.')

        self.__clean_yaml: dict = deepcopy(self.__yaml)

    # pylint: disable=too-many-branches
    # Here, quite difficult to reduce branches, due to looking in nested
    # dictionaries.

    def __setitem__(self, key: str, parameter: SetParameter):
        """Add a new key/parameter value pair.

        Parameters
        ----------
        key : `str`
            The key to assign a parameter.

        parameter : `SetParameter`
            The parameter value, which is a object.

        Raises
        ------
        KeyError
            Throw when the use try to assign a parameter value to an already
            existing key.

        ValueError
            Throw this error when the default path given to the parameter value
            is incomplete.
        """
        # Not allowing key overwriting.
        if key in self.__key:
            raise KeyError(
                "[Err##] Cannot overwrite existing key/parameter pair."
            )

        yaml: dict = self.__yaml
        set_key: list = parameter.path().split(":")
        value_set: bool = False
        param_key = set_key[-1]

        # Check the "path" of a value.
        for key_i in set_key:
            if key_i not in yaml:
                continue

            yaml = yaml[key_i]

            if key_i != param_key:
                continue

            parameter.value(yaml)
            value_set = True

        is_pop = True

        # Deleting validated parameters in the YAML file.
        while set_key != [] and value_set and is_pop:
            clean_yaml: dict = self.__clean_yaml
            is_pop = None

            # Parse the YAML path parameter.
            for key_i in set_key:
                # Last value detected.
                if key_i == param_key:
                    # Delete a value in the `clean_yaml` and pop a value in the
                    # YAML path.
                    del clean_yaml[key_i]
                    set_key.remove(key_i)

                    is_pop = True

                    break

                # Empty path detected.
                if clean_yaml[key_i] == {}:
                    # Delete a value in the `clean_yaml` and pop a value in the
                    # YAML path.
                    del clean_yaml[key_i]
                    set_key.remove(key_i)

                    is_pop = True

                    break

                clean_yaml = clean_yaml[key_i]

        if self.__verbose:
            if value_set:
                print(f'> Value set for "{parameter.path()}".')
            else:
                print(
                    f'> Path "{parameter.path()}" not found in the '
                    "parameter file, keeping the default value."
                )

        if isinstance(parameter.value(), dict):
            raise ValueError(
                f'[Err##] The path "{parameter.path()}" is '
                "incomplete, error."
            )

        parameter.check_error()

        self.__key += [key]
        self.__value += [parameter.value()]

        if parameter.category() in self.__category:
            self.__category[parameter.category()] += [
                (parameter.path(), parameter.value())
            ]
        else:
            self.__category[parameter.category()] = [
                (parameter.path(), parameter.value())
            ]

    # pylint: enable=too-many-branches

    def __getitem__(self, key: str) -> SetParameter:
        """Return a parameter value corresponding to a given key.

        Parameters
        ----------
        key : `str`
            The key to fetch a parameter.

        Returns
        -------
        `SetParameter`
            The fetched parameter.
        """
        if key not in self.__key:
            raise KeyError(f"[Err##] The key {key} does not exist.")

        return self.__value[self.__key.index(key)]

    def keys(self) -> list:
        """Return keys linked to this object.

        Returns
        -------
        `list`
            The keys.
        """
        return self.__key

    def values(self) -> list:
        """Return parameters values linked to this object.

        Returns
        -------
        `list`
            The values.
        """
        return self.__value

    def items(self) -> zip:
        """Return keys, paired to their parameters values, linked to this
        object.

        Returns
        -------
        `zip`
            The pairs key/value.
        """
        return zip(self.__key, self.__value)

    def clean(self):
        """Delete the parsed ".yaml" file.

        Raises
        ------
        `ValueError`
            Throw an exception if a value in the YAML file have not been added.
        """
        del self.__yaml, self.__verbose

        if self.__clean_yaml != {}:
            raise ValueError(
                "[Err##] The YAML have been parsed, but there "
                "are unassigned values. Please check the input "
                "files and its indentation. The remaining values "
                f"are:\n{dump(self.__clean_yaml)}"
            )

    def __str__(self) -> str:
        """Redefine the `print()` behaviour of this class.

        Returns
        -------
        `str`
            The message to print.
        """
        to_print: str = ""

        for key, pair in self.__category.items():
            to_print += f"\033[7m {key.upper()} \033[0m\n"

            for path, value in pair:
                to_print += f"- {path} = {value}\n"

        return to_print[:-1]


if __name__ == "__main__":
    yaml_parser = ParseYaml("parameters.yml", False)

    yaml_parser["h_bond_mu"] = SetParameter(
        3.0,
        (int, float),
        "statistical_energy_function:h_bond:mu",
        "Energy parameters",
    )

    yaml_parser["h_bond_sigma"] = SetParameter(
        0.15,
        (int, float),
        "statistical_energy_function:h_bond:sigma",
        "Energy parameters",
    )

    yaml_parser["hydrophobic_mu"] = SetParameter(
        10, (int, float), "other:gaussian_scalar", "Other"
    )

    print(yaml_parser)
