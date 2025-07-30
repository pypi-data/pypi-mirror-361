"""Contains a class with strategy to trim a grid based on sphere."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_trimming import StrategyTrimming

# pylint: disable=too-few-public-methods
# Trimming class that does not need a lot of method.


class StrategySphereTrimming(StrategyTrimming):
    """A class to define strategies to trim a grid based on sphere.

    Inheritance
    -----------
    This class is the child of `StrategyTrimming`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def trim_box(self, grid_object):
        """Trim a grid mask based on sphere trimming method.

        Parameters
        ----------
        grid_object : `Grid`
            The grid object to access all attributes.
        """
        cog: np.ndarray = np.array(
            [
                grid_object.yaml["box_center_x"],
                grid_object.yaml["box_center_y"],
                grid_object.yaml["box_center_z"],
            ]
        )

        distance = np.linalg.norm(grid_object.trimming_coord - cog, axis=-1).T

        grid_object.mask[distance > grid_object.yaml["box_radius"]] = True


# pylint: enable=too-few-public-methods
