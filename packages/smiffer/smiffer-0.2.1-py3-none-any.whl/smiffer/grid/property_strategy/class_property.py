"""Contains a abstract class to define strategies to fill a grid with different
properties.
"""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [A]
from abc import abstractmethod, ABC

# [N]
import numpy as np


class StrategyProperty(ABC):
    """An abstract base class for defining strategies to fill a grid with
    properties.

    Attributes
    ----------
    self.__name : `str`
        Name of the computed property.

    self._atom_constant : `AtomConstant`
        The atom constant object to access different constant.
    """

    def __init__(self, name: str, atom_constant):
        """Define the strategy for property computation.

        Parameters
        ----------
        name : `str`
            Name of the property.

        atom_constant : `AtomConstant`
            An object containing constant linked to atoms.
        """
        self._name: str = name
        self._atom_constant = atom_constant

    def __str__(self) -> str:
        """Redefine `print()` comportement.

        Returns
        -------
        `str`
            The new message to print.
        """
        to_print: str = (
            f'Current used property is "{self._name}". Linked '
            "to an atom_constant object. "
            f"{self._atom_constant}."
        )

        return to_print

    def name(self) -> str:
        """`self.__name` getter.

        Returns
        -------
        `str`
            The property name.
        """
        return self._name

    @abstractmethod
    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Define an abstract method in order to fill a grid with given
        properties.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.

        Returns
        -------
        None
            To skip an iteration.
        """
