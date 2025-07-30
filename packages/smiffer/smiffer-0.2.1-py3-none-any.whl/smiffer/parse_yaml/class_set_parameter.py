"""Contains a class in order to contain parameters for the `YamlParser` class.
"""


__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


class SetParameter:
    """To create a parameter.

    Attributes
    ----------
    self.__value : `any`
        The value linked to the parameter.

    self.__error : `dict`
        Errors to check if the parameter is well set.

    self.__typing : `list | any`
        The typing of the parameter value.

    self.__path : `str`
        Where to find the parameter value in the `.yaml` file.

    self.__category : `str`
        The parameter category.
    """

    # pylint: disable=too-many-arguments
    # Object needs these 5 parameters to be correctly set up.
    def __init__(
        self,
        default_value: any,
        typing: "list | any",
        path: str,
        category: str,
        error: dict = None
    ):
        """Initialize a SetParameter object.

        Parameters
        ----------
        default_value : `any`
            A default value if the user does not specify one.

        typing : `list | any`
            The expected type of the value.

        path : `str`
            The "path" to follow in the `.yml` file. If the yml file is:

            ```yml
            box:
                extra_size: 5
            ```

            The path to `extra_size` is "box:extra_size".

        category : `str`
            The category to include this parameter in.

        error : `dict`, optional
            A dictionary with error to verify. Key can be:
            - "inferior": The user's value must be superior or equal to this
                          given value (user_value ≥ this_value).
            - "set": The user's value must be included in the given list.
            - "length": The user's value length must be the same as is the
                        typing parameter. If `typing = [int, int]`, the
                        expected length is 2.If `typing = [[int, int]]`, the
                        expected length is 1 then 2.

            By default, set to None.
        """
        self.__value: any = default_value
        self.__error: dict = error
        self.__typing: "list | any" = typing
        self.__path: str = path
        self.__category: str = category

    # pylint: enable=too-many-arguments

    def check_error(self):
        """Check, in function of what is indicated in `self.__error`, if
        everything is correct for the user's given value.

        Raises
        ------
        ValueError
            A value have a type, a length or does not checked a given
            condition.
        """
        # Convert the "none" string into a None (NoneType).
        if isinstance(self.__value, str):
            if self.__value.strip().lower() == "none":
                self.__value = None

        if None not in [self.__error, self.__value]:
            # Checking that the user's value is inferior to a threshold.
            if "inferior" in self.__error:
                if self.__value < self.__error["inferior"]:
                    raise ValueError(f"[Err##] Parameter \"{self.__path}\""
                                     " cannot be inferior to "
                                     f"{self.__error['inferior']}.")

            # Checking if the user's value is included in a given finish set.
            if "set" in self.__error:
                if self.__value not in self.__error["set"]:
                    raise ValueError(f"[Err##] Parameter \"{self.__path}\" "
                                     "has to be included in "
                                     f"{self.__error['set']}.")

            # Check if the user's value, which should be a list, have the
            # correct length.
            if "length" in self.__error:
                if not self.__length_good(self.__value, self.__typing):
                    raise ValueError("[Err##] Parameter "
                                     f"\"{self.__path}\" have a length "
                                     "problem. Please check that the list "
                                     "respects the next format: "
                                     f"\"{self.__typing}\".")

        # Check if the user's value type is correct.
        if isinstance(self.__typing, list):
            if not self.__type_good(self.__value, self.__typing):
                raise TypeError(f"[Err##] Parameter \"{self.__path}\" "
                                f"has to be of type: \"{self.__typing}\"")
        else:
            if not isinstance(self.__value, self.__typing):
                raise TypeError(f"[Err##] Parameter \"{self.__path}\" "
                                f"has to be of type: \"{self.__typing}\"")

    def __length_good(
        self,
        value: "list | any",
        expect_len: "list | any"
    ) -> bool:
        """Check if the expect length is good in `value`.

        Parameters
        ----------
        value : `list | any`
            The list to check the length of.

        expect_len : `list | any`
            The list of the expected length.

        Returns
        -------
        `bool`
            `True` if the length is good, `False` otherwise.
        """
        # We check that we still have a list.
        if isinstance(expect_len, list):
            # We check that value is a list.
            if isinstance(value, list):
                # Returning False when the length does not match.
                if len(value) != len(expect_len):
                    return False
            # value should be a lst and is not, returning False.
            else:
                return False
        # No more list = ending.
        else:
            return True

        for i, err_i in enumerate(expect_len):
            # Checking each sub-list and sub-sub-list and […].
            if not self.__length_good(value[i], err_i):
                return False

        # All lengths were checked and are good.
        return True

    def __type_good(self, value: "list | any", typing: "list | type") -> bool:
        """Recursing through to see if the type in `value` is the same as
        define in `typing`.

        Parameters
        ----------
        value : `list | any`
            A list or a value to check.

        typing : `list | type`
            A list or the type to compare.

        Returns
        -------
        bool
            `True` if the type is good, `False` otherwise.
        """
        # We have no more list, checking if the type matches.
        if not isinstance(typing, list):
            return isinstance(value, typing)

        # Value should be a list and is not, returning False.
        if not isinstance(value, list):
            return False

        for i, type_i in enumerate(typing):
            # Checking each sub-list and sub-sub-list and […].
            if not self.__type_good(value[i], type_i):
                return False

        # Everything was checked all is good.
        return True

    def value(self, setter: any = None) -> any:
        """Getter or setter of attributes `__value`.

        Parameters
        ----------
        setter : `any`, optional
            If a value is given, the method is not any more a getter. It become
            a setter of `self.__value`. By default None, so is a getter.

        Returns
        -------
        `any`
            `__value`'s value.
        """
        # If None, is a getter. Else, is a setter.
        if setter is None:
            return self.__value

        # Setter.
        self.__value = setter

        # No value to return.
        return None

    def path(self) -> any:
        """Getter of attributes `__path`.

        Returns
        -------
        `any`
            `__path`'s value.
        """
        return self.__path

    def category(self) -> any:
        """Getter of attributes `__category`.

        Returns
        -------
        `any`
            `__category`'s value.
        """
        return self.__category

    def __str__(self) -> str:
        """Redefine the `print()` comportment of this class.

        Returns
        -------
        `str`
            The message to print.
        """
        to_print = f"Parameter \"{self.__path}\" is set to {self.__value}."
        return to_print


if __name__ == "__main__":
    h_bond_mu = SetParameter(
        3.0,
        (int, float),
        "statistical_energy_function:h_bond:mu",
        "Energy parameters",
        {"inferior": 0}
    )

    print(h_bond_mu)
