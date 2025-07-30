"""Assemble a grid in order to launch the algorithm."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


# [C]
from .class_grid import Grid
from .class_grid_factory import GridFactory

# [K]
from .kernel import OccupancyKernel

# [P]
from .property_strategy import StrategyApbs
from .property_strategy import StrategyHydrophobic
from .property_strategy import StrategyHBond
from .property_strategy import StrategyPiStacking

# [T]
from .trimming_strategy import StrategyOccupancyTrimming
from .trimming_strategy import StrategySphereTrimming
from .trimming_strategy import StrategyRndsTrimming

# [U]
from ..utils import AtomConstant


def grid(yaml, argument, date: str):
    """Assemble a grid and compute properties inside it.

    Parameters
    ----------
    yaml : `ParseYaml`
        The parsed `.yml` file.

    argument : `ArgumentParser`
        The parsed given arguments.

    date : `str`
        The launching time.
    """
    grid_factory = GridFactory(yaml=yaml, argument=argument)
    grid_object: Grid = grid_factory.create_grid()

    # Adding properties strategies.
    if yaml["flag_h_bond_acceptor"]:
        grid_object["property"] += [
            StrategyHBond(
                name="h_b_acceptor",
                atom_constant=AtomConstant(),
                key="h_b_acceptor",
            )
        ]

    if yaml["flag_h_bond_donor"]:
        grid_object["property"] += [
            StrategyHBond(
                name="h_b_donor", atom_constant=AtomConstant(), key="h_b_donor"
            )
        ]

    if yaml["flag_hydrophobic"]:
        grid_object["property"] += [
            StrategyHydrophobic(
                name="hydrophobic", atom_constant=AtomConstant(), 
                macro_type=yaml["other_macromolecule"], key="hydrophobic"
            )
        ]

    if yaml["flag_hydrophilic"]:
        grid_object["property"] += [
            StrategyHydrophobic(
                name="hydrophilic", atom_constant=AtomConstant(), 
                macro_type=yaml["other_macromolecule"], key="hydrophilic"
            )
        ]

    if yaml["flag_pi_stacking"]:
        grid_object["property"] += [
            StrategyPiStacking(name="pi_stacking", atom_constant=AtomConstant())
        ]

    if argument.apbs is not None:
        grid_object["property"] += [
            StrategyApbs(
                name="apbs",
                atom_constant=AtomConstant(),
                path=argument.apbs,
            )
        ]

    # Adding trimming strategies.
    if yaml["trimming_sphere"]:
        grid_object["trimming"] += [StrategySphereTrimming()]

    if yaml["trimming_occupancy"]:
        # Creating a kernel.
        occupancy_kernel: OccupancyKernel = OccupancyKernel(
            radius=yaml["trimming_distance_atom_minimum"],
            delta=grid_object.delta,
        )

        grid_object["trimming"] += [
            StrategyOccupancyTrimming(kernel=occupancy_kernel)
        ]

    if yaml["trimming_rnds"]:
        grid_object["trimming"] += [StrategyRndsTrimming()]

    grid_object.launch_trimming()
    grid_object.compute_property(date=date)
