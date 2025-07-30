"""Contains a class with strategy to fill a grid with pi stacking properties."""

# pylint: disable=duplicate-code
# THERE IS NO DUPLICATE CODE, THESE ARE IMPORT PYLINT!!!

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = [
    "diego.barqueromorera@studenti.unitn.it",
    "lucas.rouaud@gmail.com",
]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_property import StrategyProperty

# [G]
from ..class_stamp import Stamp

# [K]
from ..kernel import BivariateGaussianKernel

# pylint: enable=duplicate-code


class StrategyPiStacking(StrategyProperty):
    """A class for defining strategies to fill a grid with pi stacking
    properties.

    Inheritance
    -----------
    This class is the child of `StrategyProperty`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Populate a grid following H-bond properties.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        radius: float = (
            grid_object.yaml["function_pi_stacking_mu"][1]
            + grid_object.yaml["function_pi_stacking_sigma"][1][1] ** (1 / 2)
            * grid_object.yaml["other_gaussian_kernel_scalar"]
        )

        pi_stacking_kernel: BivariateGaussianKernel = BivariateGaussianKernel(
            radius=radius,
            delta=grid_object.delta,
            v_mu=np.array(grid_object.yaml["function_pi_stacking_mu"]),
            # Pre-inversing the matrix.
            v_sigma=np.linalg.inv(
                grid_object.yaml["function_pi_stacking_sigma"]
            ),
            is_stacking=True,
        )

        stamp: Stamp = Stamp(
            grid=grid,
            grid_origin=grid_object.coord[0],
            delta=grid_object.delta,
            kernel=pi_stacking_kernel,
        )

        parsed_residue: dict = {}

        for atom in grid_object.molecule:
            if atom.resname not in self._atom_constant["aromatic"]:
                continue

            # In order to not check multiple time the same residue.
            if atom.resname not in parsed_residue:
                parsed_residue[atom.resname] = []

            atom_id: tuple = (atom.resid, atom.chainID)

            # Skip if already parsed.
            if atom_id in parsed_residue[atom.resname]:
                continue

            parsed_residue[atom.resname] += [atom_id]

            select: str = (
                f"resid {atom.resid} "
                f"and name {self._atom_constant['aromatic'][atom.resname]}"
            )

            if atom.chainID is not None:
                select += f" and chainID {atom.chainID}"

            res_atom = grid_object.molecule.select_atoms(select)

            if len(res_atom) < 3:
                continue

            # Because the pi stacking kernel is a "donut" and have a
            # orientation.
            pi_stacking_kernel.refresh_orientation(
                coordinate=res_atom.positions[:3]
            )
            stamp.refresh_orientation(kernel=pi_stacking_kernel.kernel())

            stamp.stamp_kernel(center=res_atom.center_of_geometry())
