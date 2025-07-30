"""Contain an abstract class to create kernels."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [A]
from abc import ABC

# [N]
import numpy as np


class Kernel(ABC):
    """An abstract class to create kernel.

    Attributes
    ----------
    self._kernel_resolution : `np.ndarray`
        The kernel resolution.

    self._kernel : `np.ndarray`
        The kernel to stamp on a grid.

    self._distance : `np.ndarray`
        A matrix of distances between the kernel center and all other points
        arround it.
    """

    def __init__(
        self,
        radius: float,
        delta: np.ndarray,
        d_type: type,
    ):
        """Instanciates a kernel.

        Parameters
        ----------
        radius : `float`
            The kernel size.

        delta : `np.ndarray`
            Delta linked to the grid to stamp the kernel on.

        d_type : `type`
            The data type for the kernel.
        """
        self._kernel_resolution: np.ndarray = (
            np.ceil(radius / delta) * 2 + 1
        ).astype(int)

        self._kernel: np.ndarray = np.zeros(
            shape=self._kernel_resolution, dtype=d_type
        )

        center: np.ndarray = np.floor(self._kernel_resolution / 2) * delta

        self._distance: np.ndarray = np.linalg.norm(
            np.indices(self._kernel_resolution).T * delta - center, axis=-1
        ).T

    def kernel(self) -> np.ndarray:
        """Getter of the generated kernel.

        Returns
        -------
        `np.ndarray`
            The kernel.
        """
        return self._kernel

    def kernel_resolution(self) -> np.ndarray:
        """Getter of the kernel resolution.

        Returns
        -------
        `np.ndarray`
            The kernel resolution.
        """
        return self._kernel_resolution
