"""Contains a class with strategy to fill a grid with hydrophobic properties."""

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
from ..kernel import GaussianKernel

# pylint: enable=duplicate-code


class StrategyHydrophobic(StrategyProperty):
    """A class for defining strategies to fill a grid with hydrophobic
    properties.

    Inheritance
    -----------
    This class is the child of `StrategyProperty`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def __init__(
        self, name: str, atom_constant: object, macro_type: str, key: str
    ):
        super().__init__(name, atom_constant)

        if macro_type not in ["protein", "nucleic"]:
            raise ValueError(
                f'[Err##] macro_type "{macro_type}" not accepted. List of '
                'accepted macro_types are "["protein", '
                '"nucleic"]".'
            )

        if key not in ["hydrophobic", "hydrophilic"]:
            raise ValueError(
                f'[Err##] key "{key}" not accepted. List of '
                'accepted keys are "["hydrophobic", '
                '"hydrophilic"]".'
            )

        self._isNucleic: bool = macro_type == "nucleic"
        self._key: str = key

    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Populate a grid following H-bond properties.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        do_hydrophobic: bool = self._key == "hydrophobic"

        if do_hydrophobic:
            radius: float = (
                grid_object.yaml["function_hydrophobic_mu"]
                + grid_object.yaml["function_hydrophobic_sigma"]
                * grid_object.yaml["other_gaussian_kernel_scalar"]
            )

            kernel: GaussianKernel = GaussianKernel(
                radius=radius,
                delta=grid_object.delta,
                v_mu=grid_object.yaml["function_hydrophobic_mu"],
                v_sigma=grid_object.yaml["function_hydrophobic_sigma"],
            )

        else:
            radius: float = (
                grid_object.yaml["function_hydrophilic_mu"]
                + grid_object.yaml["function_hydrophilic_sigma"]
                * grid_object.yaml["other_gaussian_kernel_scalar"]
            )

            kernel: GaussianKernel = GaussianKernel(
                radius=radius,
                delta=grid_object.delta,
                v_mu=grid_object.yaml["function_hydrophilic_mu"],
                v_sigma=grid_object.yaml["function_hydrophilic_sigma"],
            )

        stamp: Stamp = Stamp(
            grid=grid,
            grid_origin=grid_object.coord[0],
            delta=grid_object.delta,
            kernel=kernel,
        )

        for atom in grid_object.molecule:
            # atom is part of a protein
            if not self._isNucleic:
                mul_factor = self._atom_constant["ww_scale"][atom.resname]

            # atom is in the nitrogenous base (RNA)
            elif (
                atom.name in self._atom_constant["nucleic_bases"][atom.resname]
            ):
                mul_factor = self._atom_constant["ww_scale"][atom.resname]

            # atom is part of the phosphate backbone (RNA)
            elif atom.name in self._atom_constant["backbone_phosphate"]:
                mul_factor = self._atom_constant["hphil_rna_phosphate"]

            # atom is part of the sugar (RNA)
            elif atom.name in self._atom_constant["backbone_sugar"]:
                mul_factor = self._atom_constant["hphil_rna_sugar"]

            # unknown atom type
            else:
                continue

            # skip hydrophilic atoms in the hydrophobic grid
            if do_hydrophobic:
                if mul_factor < 0:
                    continue

            # skip hydrophobic atoms in the hydrophilic grid
            elif mul_factor > 0:
                continue

            stamp.stamp_kernel(
                center=atom.position,
                factor=np.abs(mul_factor),
            )
