"""Contains a class with strategy to trim a grid based on occupancy."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [C]
from .class_trimming import StrategyTrimming

# [G]
from ..class_stamp import Stamp

# pylint: disable=too-few-public-methods
# Trimming class that does not need a lot of method.


class StrategyOccupancyTrimming(StrategyTrimming):
    """A class to define strategies to trim a grid based on occupancy.

    Inheritance
    -----------
    This class is the child of `StrategyTrimming`. Check this one for other
    **attributes** and **methods** definitions.

    Attributes
    ----------
    self.__kernel : `OccpancyKernel`
        The occupancy boolean kernel.
    """

    def __init__(self, kernel):
        """Trim a grid based on occupancy.

        Parameters
        ----------
        kernel : `OccupancyKernel`
            The occupancy boolean kernel.
        """
        self.__kernel = kernel

    def trim_box(self, grid_object):
        """Trim a grid mask based on occupancy trimming method.

        Parameters
        ----------
        grid_object : `Grid`
            The grid object to access all attributes.
        """
        stamp: Stamp = Stamp(
            grid=grid_object.mask,
            grid_origin=grid_object.coord[0],
            delta=grid_object.delta,
            kernel=self.__kernel,
        )

        for atom in grid_object.molecule_broad:
            stamp.stamp_kernel(center=atom.position)


# pylint: enable=too-few-public-methods
