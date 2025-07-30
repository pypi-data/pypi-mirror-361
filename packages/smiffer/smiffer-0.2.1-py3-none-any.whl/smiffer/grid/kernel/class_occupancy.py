"""Contain a class for occupancy kernel (boolean)."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_kernel import Kernel


class OccupancyKernel(Kernel):
    """A class to create a kernel based on sphere.

    Inheritance
    -----------
    This class is the child of `Kernel`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def __init__(
        self,
        radius: float,
        delta: np.ndarray,
    ):
        """Instanciates a sphere kernel.

        Parameters
        ----------
        radius : `float`
            The kernel size.

        delta : `np.ndarray`
            Delta linked to the grid to stamp the kernel on.
        """
        super().__init__(radius, delta, bool)

        self._kernel[self._distance < radius] = 1
