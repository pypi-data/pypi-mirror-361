"""Contains a class with strategy to fill a grid with electrostatic properties."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [G]
from gridData import Grid

# [N]
import numpy as np

# [S]
from scipy import interpolate

# [C]
from .class_property import StrategyProperty


class StrategyApbs(StrategyProperty):
    """A class for defining strategies to fill a grid with electrostatic
    properties.

    Inheritance
    -----------
    This class is the child of `StrategyProperty`. Check this one for other
    **attributes** and **methods** definitions.

    Attributes
    ----------
    self.__path : `str`
        The APBS OpenDX file path.

    self.__grid : `np.ndarray`
        The grid where to set APBS values.
    """

    def __init__(self, name: str, atom_constant: object, path: str):
        """Define the strategy for electrostatic properties computation.

        Parameters
        ----------
        name : `str`
            Name of the property.

        atom_constant : `AtomConstant`
            An object containing constant linked to atoms.

        path : `str`
            A path to the APBS computed grid.

        Raises
        ------
        ValueError
            _description_
        """
        super().__init__(name, atom_constant)

        self.__path: str = path
        self.__grid: np.ndarray = np.array([])

    def populate_grid(self, grid: np.ndarray, grid_object) -> None:
        """Populate a grid following electrostatic properties. The population
        method by interpolation from Scipy is currently only being used for
        APBS results (as it's the only PPS currently implemented). But it can
        be generalized to any other grid obtained by external means.

        Parameters
        ----------
        grid: `np.ndarray`
            The grid to fill.

        grid_object : `Grid`
            The grid object to access all attributes.
        """
        if self.__grid.size != 0:
            self.log_grid(yaml=grid_object.yaml)
            return None

        apbs = Grid(self.__path)

        apbs_coord: np.ndarray = np.array(
            [apbs.origin, apbs.origin + apbs.delta * apbs.grid.shape]
        ).T

        slicing: tuple = (
            slice(
                grid_object.coord[0][0],
                grid_object.coord[1][0],
                complex(0, grid_object.resolution[0]),
            ),
            slice(
                grid_object.coord[0][1],
                grid_object.coord[1][1],
                complex(0, grid_object.resolution[1]),
            ),
            slice(
                grid_object.coord[0][2],
                grid_object.coord[1][2],
                complex(0, grid_object.resolution[2]),
            ),
        )

        grid[:, :, :] = interpolate.RegularGridInterpolator(
            points=(
                np.linspace(*apbs_coord[0], apbs.grid.shape[0]),
                np.linspace(*apbs_coord[1], apbs.grid.shape[1]),
                np.linspace(*apbs_coord[2], apbs.grid.shape[2]),
            ),
            values=apbs.grid,
            bounds_error=False,
            fill_value=0,
        )(np.mgrid[slicing].T).T

        self.__grid = grid

        return None

    def log_grid(self, yaml):
        """Modify the APBS grid to apply log_10 on it.

        Parameters
        ----------
        yaml : `ParseYaml`
            A parsed yaml.
        """
        self._name = "log_apbs"

        array_filter: np.ndarray = self.__grid > 0

        self.__grid[array_filter] = np.log10(self.__grid[array_filter])
        self.__grid[~array_filter] = -np.log10(self.__grid[~array_filter])

        self.__grid = np.clip(self.__grid, *yaml["apbs_cut_off"])

        self.__grid -= yaml["apbs_cut_off"][0]
        self.__grid *= 2
        self.__grid[~array_filter] *= -1
