"""Contain a class to stamp gaussian on a given grid."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np


class Stamp:
    """A class to stamp kernel on a grid on a given position.

    Attributes
    ----------
    self.__grid : `np.ndarray`
        The grid on which to apply gaussian.

    self.__resolution: `np.ndarray`
            The grid resolution.

    self.__grid_origin : `np.ndarray`
        The grid origin. This corresponds to the coordinate in [0, 0, 0] in
        the grid.

    self.__delta : `np.ndarray`
        The delta of the grid.

    self.__kernel_resolution : `np.ndarray`
        The resolution of the kernel.

    self.__kernel : `Kernel`
        The kernel.
    """

    def __init__(
        self,
        grid: np.ndarray,
        grid_origin: np.ndarray,
        delta: np.ndarray,
        kernel,
    ):
        """Instantiates a kernel to apply gaussian on a given grid.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid on which to apply gaussian.

        grid_origin : `np.ndarray`
            The grid origin. This corresponds to the coordinate in [0, 0, 0] in
            the grid.

        delta : `np.ndarray`
            The delta of the grid.

        kernel : `np.ndarray`
            The kernel to use.
        """
        self.__grid: np.ndarray = grid
        self.__resolution: np.ndarray = np.array(grid.shape)
        self.__grid_origin: np.ndarray = grid_origin

        self.__delta: np.ndarray = delta

        self.__kernel: np.ndarray = kernel.kernel()
        self.__kernel_resolution: np.ndarray = kernel.kernel_resolution()

    def refresh_orientation(self, kernel: np.ndarray):
        """Refresh the kernel orientation.

        Parameters
        ----------
        kernel : `np.ndarray`
            The new kernel to apply gaussian on the defined grid.
        """
        self.__kernel = kernel

    def stamp_kernel(self, center: np.ndarray, factor: float = None):
        """Stamp a kernel on a given position on the defined grid.

        Parameters
        ----------
        center : `np.ndarray`
            The position where to stamp the kernel.

        factor : `float`, optional
            A multiplication factor to change the kernel's gaussian intensity.
        """
        # Computing the origin on the grid to stamp the kernel on it.
        origin: np.ndarray = center
        origin -= self.__delta * self.__kernel_resolution / 2
        origin = np.round((origin - self.__grid_origin) / self.__delta).astype(
            int
        )

        grid_index: np.ndarray = np.array(
            [origin, origin + self.__kernel_resolution]
        )

        kernel_index: np.ndarray = np.array(
            [[0, 0, 0], self.__kernel_resolution]
        )

        # Switching between min and max indices.
        for i in [0, 1]:
            # Resizing the grid when the kernel is outside (smaller).
            array_filter: np.ndarray = grid_index[i] < 0
            kernel_index[i][array_filter] = -grid_index[i][array_filter]
            grid_index[i][array_filter] = 0

            # Resizing the grid when the kernel is outisde (bigger).
            array_filter: np.ndarray = grid_index[i] > self.__resolution
            kernel_index[i][array_filter] = (
                self.__resolution[array_filter] - grid_index[i][array_filter]
            )
            grid_index[i][array_filter] = self.__resolution[array_filter]

        # Applying computed indexes.
        grid: np.ndarray = self.__grid[
            grid_index[0][0] : grid_index[1][0],
            grid_index[0][1] : grid_index[1][1],
            grid_index[0][2] : grid_index[1][2],
        ]

        kernel: np.ndarray = self.__kernel[
            kernel_index[0][0] : kernel_index[1][0],
            kernel_index[0][1] : kernel_index[1][1],
            kernel_index[0][2] : kernel_index[1][2],
        ]

        # Stamping the kernel.
        if factor is not None:
            grid += kernel * factor
        else:
            grid += kernel
