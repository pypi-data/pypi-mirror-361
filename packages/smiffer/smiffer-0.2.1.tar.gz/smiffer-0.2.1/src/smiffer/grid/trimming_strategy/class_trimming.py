"""Contains a abstract class to define strategies to trim a grid."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [A]
from abc import abstractmethod

# pylint: disable=too-few-public-methods
# Trimming class that does not need a lot of method.


class StrategyTrimming:
    """A abstract class to define strategies to trim a grid."""

    @abstractmethod
    def trim_box(self, grid_object):
        """Define a abstract method in order to trim a grid.

        Parameters
        ----------
        grid_object : `Grid`
            The grid object to access all attributes.
        """


# pylint: enable=too-few-public-methods
