"""Contain a class to create kernel based on gaussian."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_kernel import Kernel


class GaussianKernel(Kernel):
    """A class to create a kernel based on gaussian.

    Inheritance
    -----------
    This class is the child of `Kernel`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def __init__(
        self,
        radius: float,
        delta: np.ndarray,
        v_mu: float,
        v_sigma: float,
    ):
        """Instanciates a gaussian kernel.

        Parameters
        ----------
        radius : `float`
            The kernel size.

        delta : `np.ndarray`
            Delta linked to the grid to stamp the kernel on.

        v_mu : `float`
            The mu parameter for the gaussian.

        v_sigma : `float`
            The sigma parameter for the gaussian.

        """
        super().__init__(radius, delta, np.half)

        v_mu = v_mu - self._distance

        # Compute vectors.
        v_sigma = 1 / (v_sigma**2)

        # Compute exponential function.
        self._kernel = - np.exp(-(1 / 2) * np.power(v_mu, 2) * v_sigma)
