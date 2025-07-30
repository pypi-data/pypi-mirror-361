"""Contain a class for special gaussian (matrix)."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_kernel import Kernel


class BivariateGaussianKernel(Kernel):
    """
    TODO: Refactor name and update docs -> The bivariate gaussian now also applies for HBonds, not only stacking.
    A class to create a kernel based on "stacking" gaussian.

    Inheritance
    -----------
    This class is the child of `Kernel`. Check this one for other
    **attributes** and **methods** definitions.

    Attributes
    ----------
    self.__shift_coordinate : `np.ndarray`
        The coordinates shifted in order to correspond to the system one.
    """

    def __init__(
        self,
        radius: float,
        delta: np.ndarray,
        v_mu: np.ndarray,
        v_sigma: np.ndarray,
        is_stacking: bool
    ):
        """Instanciates a kernel for stacking gaussian.

        Parameters
        ----------
        radius : `float`
            The kernel size.

        delta : `np.ndarray`
            Delta linked to the grid to stamp the kernel on.

        v_mu : `np.ndarray`
            The mu parameter for the gaussian.

        v_sigma : `np.ndarray`
            The sigma parameter for the gaussian.

        is_stacking : `bool`
            If the kernel is for stacking (True) or for HBonds (False).
        """
        super().__init__(radius, delta, np.half)

        self.__shift_coordinate: np.ndarray = (
            np.indices(self._kernel_resolution).T * delta
        )

        self.__shift_coordinate -= np.floor(self._kernel_resolution / 2) * delta

        self.__mu: np.ndarray = v_mu
        self.__sigma: np.ndarray = v_sigma
        self.__is_stacking: bool = is_stacking

    def refresh_orientation(self, coordinate: np.ndarray):
        """Refresh the kernel orientation.

        Parameters
        ----------
        coordinate : `np.ndarray`
            The coordinates of three points in the aromatic ring (in the case of stacking) or 
            the coordinates of antecedent-hbond_atom pair (in the case of HBond).
        """
        ref_vector: np.ndarray
        if self.__is_stacking:
            # StrategyPiStacking provides a group of three points to compute the reference vector
            ref_vector = self.__get_normal_vector(coordinate)
        else:
            # StrategyHBond provides the reference vector directly
            ref_vector = coordinate 
            ref_vector /= np.linalg.norm(ref_vector) # normalize
            
        beta: np.ndarray = self.__get_angle(self.__shift_coordinate, ref_vector)

        matrix: np.ndarray = np.concatenate(
            (
                np.resize(beta, list(beta.shape) + [1]),
                np.resize(self._distance, list(self._distance.shape) + [1]),
            ),
            axis=3,
        )

        self._kernel = self.__stacking_gaussian(matrix)

    def __get_normal_vector(self, coordinate: np.ndarray) -> np.ndarray:
        """Compute the normal vector from a aromatic ring, considered here as
        a plane.

        Parameters
        ----------
        coordinate : `np.ndarray`
            The coordinates of three points in the aromatic ring.

        Returns
        -------
        `np.ndarray`
            The normal vector to the aromatic cycle, considered here as a plan.
        """
        # First cross product term.
        array_a: np.ndarray = (coordinate[2] - coordinate[0]) / np.linalg.norm(
            coordinate[2] - coordinate[0]
        )

        # Second cross product term.
        array_b: np.ndarray = (coordinate[1] - coordinate[0]) / np.linalg.norm(
            coordinate[1] - coordinate[0]
        )

        normal: np.ndarray = np.cross(array_a, array_b)
        normal /= np.linalg.norm(normal)

        return normal

    def __get_angle(self, matrix: np.ndarray, vec: np.ndarray):
        """Compute an angle, in degree, between a matrix and a vector.

        Parameters
        ----------
        matrix : `np.ndarray`
            A matrix.

        vec : `np.ndarray`
            A vector.

        Returns
        -------
        `float`
            The compute angle in degree.
        """
        # Formula cos-1 [(numerator) / (denominator)]
        # a . b
        numerator: np.ndarray = np.sum(matrix * vec, axis=-1)
        # norm(a) * norm(b)
        denominator: np.ndarray = np.linalg.norm(
            matrix, axis=-1
        ) * np.linalg.norm(vec, axis=-1)

        mask = denominator == 0
        numerator[mask] = 1
        denominator[mask] = 1

        # If numerator / denominator not include in [-1, 1]; take -1 if
        # val < -1, take 1 if val > 1
        cos_val = np.clip(numerator / denominator, -1, 1)

        # Convert the angle in degree.
        angle = np.arccos(cos_val) * 180 / np.pi
        if self.__is_stacking:
            angle[angle >= 90] = 180 - angle[angle >= 90]
        else:
            angle = 180 - angle
        angle[mask] = -90

        return angle.T

    def __stacking_gaussian(
        self,
        distance: np.ndarray,
    ) -> np.ndarray:
        """Compute Gaussian diffusion on a given vector/matrix.

        Parameters
        ----------
        distance : `: np.ndarray`
            Distance between Center Of Geometry and all coordinates.

        Returns
        -------
        `np.ndarray`
            The modified array.
        """
        v_mu: np.ndarray = self.__mu - distance

        # Extract value from the vectors.
        u_x: np.ndarray = v_mu[:, :, :, 0]
        u_y: np.ndarray = v_mu[:, :, :, 1]

        # Pre-compute members of exponential function.
        to_exp_x: np.ndarray = u_x * (
            self.__sigma[0, 0] * u_x + self.__sigma[0, 1] * u_y
        )

        to_exp_y: np.ndarray = u_y * (
            self.__sigma[1, 0] * u_x + self.__sigma[1, 1] * u_y
        )

        # Compute exponential function.
        to_exp: np.ndarray = np.exp(-(1 / 2) * (to_exp_x + to_exp_y))

        return - to_exp
