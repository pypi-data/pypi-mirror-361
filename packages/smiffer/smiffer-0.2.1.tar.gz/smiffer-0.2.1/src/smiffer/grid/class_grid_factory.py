"""Contains class with strategies to fill a grid with different properties."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [M]
import MDAnalysis as md

# [N]
import numpy as np

# [G]
from .class_grid import Grid

# pylint: disable=too-few-public-methods
# This is a factory, it does not need a lot of public method.


class GridFactory:
    """Give parameters and in function of them, create a grid.

    Attributes
    ----------
    self.__yaml : `ParseYaml`
        The parsed ".yml" file.

    self.__script_arg : `ArgumentParser`
        Script arguments.

    self.__system : `md.Universe`
        The parsed protein by MDAnalysis.

    self.__grid_arg : `dict`
        A dictionary containing argument to generate a `Grid` object.

    self.__resolution_is_none : `bool`
        `True` if one resolution (x, y or z) is `None`. Else, `False`.
    """

    def __init__(self, yaml, argument):
        """Generates a grid object in function of given arguments and
        parameters.

        Parameters
        ----------
        yaml : `ParseYaml`
            The parsed yaml file with parameters.

        argument : `ArgumentParser`
            The parsed arguments.

        Raises
        ------
        ValueError
            Thrown when the parameters "box_area_mode" is wrong or when there
            is no atoms that are selected.
        """
        self.__yaml = yaml
        self.__script_arg = argument

        # Defining the system.
        self.__system: md.Universe = md.Universe(self.__script_arg.input)
        self.__grid_arg: dict = {}

        self.__resolution_is_none: bool = (
            self.__yaml["box_resolution_x"]
            and self.__yaml["box_resolution_y"]
            and self.__yaml["box_resolution_z"]
        ) is None

        # Using computation method linked to "whole" mode.
        if self.__yaml["box_area_mode"] == "whole":
            self.__whole()
        # Using computation method linked to "pocket_sphere" mode.
        elif self.__yaml["box_area_mode"] == "pocket_sphere":
            self.__pocket_sphere()
        # Throw an error when the "pocket_sphere" has a value different from the
        # expected ones. These are included in ["whole", "pocket_sphere"].
        else:
            raise ValueError(
                "[Err##] The \"box_area_mode\" in yaml file is "
                "wrong and should be included in \"[\"whole\", "
                "\"pocket_sphere\"]\". Actual value is "
                f"{self.__yaml['box_area_mode']}"
            )

        # Check the number of atoms in the made selection.
        nb_atom: int = len(self.__grid_arg["molecule"])

        if nb_atom < 1:
            raise ValueError(
                "[Err##] Applying the given parameters, no atoms "
                "in the PDB were selected. Please check the "
                "parameters or the input files."
            )

        # Print the number of selected atoms in verbose mode.
        if self.__script_arg.verbose:
            print(f"> There are {nb_atom} atoms that are selected.")

    def __whole(self):
        """Set a grid for the "whole" mode.

        Parameters
        ----------
        resolution : `np.ndarray`
            The chosen grid resolution.
        """
        pos: np.ndarray = self.__system.coord.positions

        # Min and max coordinates.
        coord: list = [
            np.min(pos, axis=0) - self.__yaml["box_extra_size"],
            np.max(pos, axis=0) + self.__yaml["box_extra_size"],
        ]

        molecule: str = self.__yaml["other_macromolecule"]

        resolution, delta = self.__resolution_delta(
            box_size=coord[1] - coord[0]
        )

        # Setting the grid parameters.
        self.__grid_arg: dict = {
            "delta": delta,
            "resolution": resolution,
            "coord": coord,
            "molecule": self.__system.select_atoms(f"{molecule} and not (name H*)"),
            "molecule_broad": self.__system.select_atoms(f"{molecule} and not (name H*)"),
        }

    def __pocket_sphere(self):
        """Set a grid for the "pocket_sphere" mode.

        Parameters
        ----------
        resolution : `np.ndarray`
            The chosen grid resolution.
        """
        cog: np.ndarray = np.array(
            [
                self.__yaml["box_center_x"],
                self.__yaml["box_center_y"],
                self.__yaml["box_center_z"],
            ]
        )

        radius: float = self.__yaml["box_radius"]

        # Make a general selection with the last parameter to change.
        # This while go from f"{x} {{}}" to "0 {}" for instance.
        select: str = (
            f"{self.__yaml['other_macromolecule']} and not (name H*) and point "
            f"{cog[0]} {cog[1]} {cog[2]} {{}}"
        )

        coord: list = [cog - radius, cog + radius]

        resolution, delta = self.__resolution_delta(
            box_size=coord[1] - coord[0]
        )

        # Setting the grid parameters.
        self.__grid_arg: dict = {
            "delta": delta,
            "resolution": resolution,
            # Min and max coordinates.
            "coord": coord,
            # Modify the last parameter to be the radius.
            "molecule": self.__system.select_atoms(select.format(radius)),
            # Modify the last parameter to be the radius + the trimming atom
            # minimum distance.
            "molecule_broad": self.__system.select_atoms(
                select.format(
                    radius + self.__yaml["trimming_distance_atom_minimum"]
                )
            ),
        }

    def __resolution_delta(self, box_size: float) -> tuple:
        """Compute the resolution and delta from the box size.

        Parameters
        ----------
        box_size : `float`
            The size of the box.

        Returns
        -------
        `tuple`
            The resolution and delta, both as `np.ndarray`.
        """
        if self.__resolution_is_none:
            delta: np.ndarray = np.array(
                [
                    self.__yaml["box_delta_x"],
                    self.__yaml["box_delta_y"],
                    self.__yaml["box_delta_z"],
                ]
            )

            resolution: np.ndarray = np.rint(box_size / delta).astype(int)
        else:
            resolution: np.ndarray = np.array(
                [
                    self.__yaml["box_resolution_x"],
                    self.__yaml["box_resolution_y"],
                    self.__yaml["box_resolution_z"],
                ]
            )

            delta: np.ndarray = box_size / resolution

        return resolution, delta

    def create_grid(self) -> Grid:
        """To obtain the grid once the factory has computed its parameters.

        Returns
        -------
        `Grid`
            The setted grid.
        """
        return Grid(
            yaml=self.__yaml, argument=self.__script_arg, **self.__grid_arg
        )


# pylint: enable=too-few-public-methods
