"""Contains a class with strategy to fill a grid with H-bond properties."""

# pylint: disable=duplicate-code
# THERE IS NO DUPLICATE CODE, THESE ARE IMPORT PYLINT!!!

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = [
    "diego.barqueromorera@studenti.unitn.it",
    "lucas.rouaud@gmail.com",
]
__copyright__ = "MIT License"

import MDAnalysis as mda

# [N]
import numpy as np

# [C]
from .class_property import StrategyProperty

# [G]
from ..class_stamp import Stamp

# [K]
from ..kernel import BivariateGaussianKernel

# pylint: enable=duplicate-code


class StrategyHBond(StrategyProperty):
    """A class for defining strategies to fill a grid with H-bond
    properties.

    Inheritance
    -----------
    This class is the child of `StrategyProperty`. Check this one for other
    **attributes** and **methods** definitions.

    Attributes
    ----------
    self.__key : `str`
        The key to switch between acceptor or donnor mode.
    """

    def __init__(self, name: str, atom_constant: object, key: str):
        """Define the strategy for H-bond properties computation.

        Parameters
        ----------
        name : `str`
            Name of the property.

        atom_constant : `AtomConstant`
            An object containing constant linked to atoms.

        key : `str`
            Which analyze to use between acceptor and donor. Respectively,
            gives the key "h_b_acceptor" or "h_b_donor" to this parameter to
            specify the wanted method.

        Raises
        ------
        ValueError
            Throw an error when the given key is not "h_b_acceptor" or
            "h_b_donor".
        """
        super().__init__(name, atom_constant)

        if key not in ["h_b_acceptor", "h_b_donor"]:
            raise ValueError(
                f'[Err##] Key "{key}" not accepted. List of '
                'accepted keys are "["h_b_acceptor", '
                '"h_b_donor"]".'
            )

        self.__key: str = key

    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Populate a grid following H-bond properties.

        Parameters
        ----------
        grid : `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        radius: float
        h_bond_kernel: BivariateGaussianKernel
        select_antecedent: callable

        if self.__key == "h_b_acceptor":
            radius = (
                grid_object.yaml["function_h_bond_acceptor_mu"][1]
                + grid_object.yaml["function_h_bond_acceptor_sigma"][1][1] ** (1 / 2)
                * grid_object.yaml["other_gaussian_kernel_scalar"]
            )

            h_bond_kernel = BivariateGaussianKernel(
                radius=radius,
                delta=grid_object.delta,
                v_mu=np.array(grid_object.yaml["function_h_bond_acceptor_mu"]),
                # Pre-inversing the matrix.
                v_sigma=np.linalg.inv(
                    grid_object.yaml["function_h_bond_acceptor_sigma"]
                ),
                is_stacking=False,
            )

            select_antecedent = self.__select_antecedent_hba

        elif self.__key == "h_b_donor":
            radius = (
                grid_object.yaml["function_h_bond_donor_mu"][1]
                + grid_object.yaml["function_h_bond_donor_sigma"][1][1] ** (1 / 2)
                * grid_object.yaml["other_gaussian_kernel_scalar"]
            )

            h_bond_kernel = BivariateGaussianKernel(
                radius=radius,
                delta=grid_object.delta,
                v_mu=np.array(grid_object.yaml["function_h_bond_donor_mu"]),
                # Pre-inversing the matrix.
                v_sigma=np.linalg.inv(
                    grid_object.yaml["function_h_bond_donor_sigma"]
                ),
                is_stacking=False,
            ) 

            select_antecedent = self.__select_antecedent_hbd

        stamp: Stamp = Stamp(
            grid=grid,
            grid_origin=grid_object.coord[0],
            delta=grid_object.delta,
            kernel=h_bond_kernel,
        )
        table_hbond: dict = self._atom_constant[self.__key]

        for res in grid_object.molecule.residues:
            res_atoms = grid_object.molecule.select_atoms(f"segid {res.segid} and resid {res.resid} and resname {res.resname}")
            hbond_pairs = table_hbond.get(res.resname)
            if hbond_pairs is None: continue # skip weird residues

            for hbond_pair in hbond_pairs:
                if not hbond_pair: continue  # skip residues without HBond pairs
                name_antecedent, name_hbond_atom = hbond_pair

                sel_antecedent = select_antecedent(res, res_atoms, name_antecedent, name_hbond_atom, grid_object)
                sel_hbond_atom = res_atoms.select_atoms(f"name {name_hbond_atom}")
                if sel_antecedent is None: continue # skip special cases

                if not sel_hbond_atom or not sel_antecedent: continue # skip residue artifacts
                antecedent_pos = np.mean(sel_antecedent.positions, axis = 0)
                hbond_atom_pos = sel_hbond_atom[0].position

                ref_vector = hbond_atom_pos - antecedent_pos

                h_bond_kernel.refresh_orientation(coordinate=ref_vector)
                stamp.refresh_orientation(kernel=h_bond_kernel.kernel())
                stamp.stamp_kernel(center=hbond_atom_pos)

    def __select_antecedent_hba(
        self, res: mda.core.groups.Residue, res_atoms: mda.core.groups.AtomGroup,
        name_antecedent: tuple, name_hbond_atom: str, grid_object
    ) -> mda.core.groups.AtomGroup:
        """Select the antecedent of a H-bond acceptor.

        Parameters
        ----------
        res : `mda.core.groups.Residue`
            The residue containing the H-bond acceptor.

        res_atoms : `mda.core.groups.AtomGroup`
            The atoms of the `res` residue.

        name_antecedent : `tuple`
            The name of the antecedent. 1 element for standard antecedent, 2 for pseudo-antecedents.

        name_hbond_atom : `str`
            The name of the H-bond acceptor.

        grid_object : `Grid`
            The grid object to access all attributes.

        Returns
        -------
        `mda.core.groups.AtomGroup`
            Group of 1 (standard antecedent) or 2 (pseudo-antecedent) atoms.
        """

        assert isinstance(name_antecedent, tuple)

        ##### standard antecedents
        if len(name_antecedent) == 1:
            return res_atoms.select_atoms(f"name {name_antecedent[0]}")

        ##### pseudo-antecedents
        if len(name_antecedent) == 2:
            name_antecedent_0, name_antecedent_1 = name_antecedent
            
            ### special case for RNA, needs to check next residue
            if name_hbond_atom == "O3'": 
                return grid_object.molecule.select_atoms(
                    f"(segid {res.segid} and resid {res.resid} and resname {res.resname} and name {name_antecedent_0}) or" +\
                    f"(segid {res.segid} and resid {res.resid + 1} " +                 f"and name {name_antecedent_1})"
                )
            
            ### other pseudo-antecedent cases
            return res_atoms.select_atoms(f"name {name_antecedent_0} {name_antecedent_1}")

        raise ValueError(f"Invalid number of antecent atoms: {name_antecedent}")

    def __select_antecedent_hbd(
        self, res: mda.core.groups.Residue, res_atoms: mda.core.groups.AtomGroup,
        name_antecedent: tuple, name_hbond_atom: str, grid_object
    ) -> mda.core.groups.AtomGroup:
        """Select the antecedent of a H-bond donor.

        Parameters
        ----------
        res : `mda.core.groups.Residue`
            The residue containing the H-bond donor.

        res_atoms : `mda.core.groups.AtomGroup`
            The atoms of the `res` residue.

        name_antecedent : `tuple`
            The name of the antecedent. 1 element for standard antecedent, 2 for pseudo-antecedents.

        name_hbond_atom : `str`
            The name of the H-bond donor.

        grid_object : `Grid`
            The grid object to access all attributes.

        Returns
        -------
        `mda.core.groups.AtomGroup`
            Group of 1 (standard antecedent) or 2 (pseudo-antecedent) atoms.
        """

        assert isinstance(name_antecedent, tuple)

        ##### pseudo-antecedents
        if len(name_antecedent) == 2:
            name_antecedent_0, name_antecedent_1 = name_antecedent
            return res_atoms.select_atoms(f"name {name_antecedent_0} {name_antecedent_1}")

        ##### standard antecedents
        if len(name_antecedent) != 1:
            raise ValueError(f"Invalid number of antecent atoms: {name_antecedent}")

        ## special case for RNA, it's a donor only if there is no next residue
        if name_hbond_atom == "O3'": 
            sel_next_res = grid_object.molecule.select_atoms(
                f"segid {res.segid} and resid {res.resid + 1}"
            )
            if len(sel_next_res) > 0: return
        
        ## special case for RNA, it's a donor only if there is no previous residue
        if name_hbond_atom == "O5'": 
            sel_prev_res = grid_object.molecule.select_atoms(
                f"segid {res.segid} and resid {res.resid - 1}"
            )
            if len(sel_prev_res) > 0: return

        ## other standard antecedent cases
        return res_atoms.select_atoms(f"name {name_antecedent[0]}")

