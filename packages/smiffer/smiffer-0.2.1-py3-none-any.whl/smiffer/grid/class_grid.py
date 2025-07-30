"""Contains class with strategies to fill a grid with different properties."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


# [M]
import MDAnalysis as md
from gridData import mrc

# [N]
import numpy as np

# [T]
from tqdm import tqdm


class Grid:
    """Define a grid to display properties to export in `.ndx` files.

    Attributes
    ----------
    self.yaml : `object`
        The parsed ".yml" file.

    self.__argument : `object`
        Script arguments.

    self.resolution : `np.ndarray`
        The resolution of the grid.

    self.delta : `np.ndarray`
        The grid deltas.

    self.coord : `list`
        Minimum and maximum coordinates of the grid.

    self.molecule : `md.Universe`
        The parsed molecule by MDAnalysis.

    self.molecule_broad : `md.Universe`
        The parsed molecule by MDAnalysis [[ plus ]], in the case of being in
        `pocket_sphere` mode and doing the occupancy trimming, a little offset,
        for better visualization rendering.

    self.mask : `np.ndarray`
        The boolean mask to trim the grid.

    self.__property : `list`
        A list containing properties methods to compute.

    self.__trimming : `list`
        A list containing trimming methods to apply on the grid.

    self.trimming_coord : `np.ndarray`
        Coordinates using the molecule as a reference. So, each coordinates in
        the grid corresponds to the true one in the molecule system.
    """

    # pylint: disable=too-many-arguments, too-many-instance-attributes
    # Special class that needs a lot of data to be set up. Using a dataclass
    # would be unnecessary, as far as it would just simply take more memory
    # for nothing.

    __KEY: list = ["property", "trimming"]

    def __init__(
        self,
        yaml,
        argument,
        resolution: np.ndarray,
        delta: np.ndarray,
        coord: list,
        molecule: md.Universe,
        molecule_broad: md.Universe,
    ):
        """Initialize a grid object.

        Parameters
        ----------
        yaml : `ParseYaml`
            The parsed ".yml" file.

        argument : `ArgumentParser`
            The parsed given arguments.
        """
        self.yaml = yaml
        self.__argument = argument
        self.resolution: np.ndarray = resolution
        self.delta: np.ndarray = delta
        self.coord: list = coord
        self.molecule: md.Universe = molecule
        self.molecule_broad: md.Universe = molecule_broad
        self.mask: np.ndarray = np.zeros(self.resolution, dtype=bool)
        self.__property: list = []
        self.__trimming: list = []

        self.trimming_coord: np.ndarray = (
            self.coord[0] + np.indices(self.resolution).T * self.delta
        )

    # pylint: enable=too-many-arguments

    def __getitem__(self, key: str) -> list:
        """Return a item linked to this object.

        Parameters
        ----------
        key : `str`
            A key between "property" or "trimming".

        Returns
        -------
        `list`
            The list linked to the asked key.

        Raises
        ------
        KeyError
            When the key is not "property" or "trimming", throw an error.
        """
        if key == "property":
            return self.__property

        if key == "trimming":
            return self.__trimming

        raise KeyError(
            f'[Err##] Key "{key}" does not exist. Only choices '
            f'are "{self.__KEY}".'
        )

    def __setitem__(self, key: str, strategy: object):
        """Define an value linked to a specific key.

        Parameters
        ----------
        key : `str`
            The key to set.

        strategy : `object`
            The properties or trimming strategies to set.

        Raises
        ------
        TypeError
            You should only do:

        ```py
        >>> object["key"] += [strategy]
        ```

        with this object, and not:

        ```py
        >>> object["key"] = [strategy]
        ```

        KeyError
            When the key is not "property" or "trimming", throw an error.
        """
        if strategy not in [self.__property, self.__trimming]:
            raise TypeError(
                '[Err##] You cannot add a strategy using "=", '
                'but only with "+=".'
            )

        if key == "property":
            self.__property: list = strategy
        elif key == "trimming":
            self.__trimming: list = strategy
        else:
            raise KeyError(
                f'[Err##] Key "{key}" does not exist. Only'
                f'choices are "{self.__KEY}".'
            )

    def launch_trimming(self):
        """Launch the trimming strategies."""
        if self.__trimming == []:
            if self.__argument.verbose:
                print("> No trimming method given.")

            return None

        for trimming in tqdm(self.__trimming, desc="   TRIMMING THE GRID"):
            trimming.trim_box(grid_object=self)

            # Delete a trimming strategy after being used.
            del trimming

        # Delete this, because it is now useless.
        del self.__trimming

        return None

    def compute_property(self, date: str):
        """Launch the properties strategies and write the OpenDX files.

        Parameters
        ----------
        atom_constant : `AtomConstant`
            An object containing constant linked to atoms.

        date : `str`
            The launching time.

        Raises
        ------
        ValueError
            No properties strategies were defined, throw an error.
        """
        if self.__property == []:
            raise ValueError(
                "[Err##] You must specify at least one property strategy."
            )

        # ======
        # Header
        # ======

        # Adding grid data.
        resolution: str = (
            f"{self.resolution[0]} {self.resolution[1]} "
            f"{self.resolution[2]}"
        )

        format: str = self.yaml["other_volume_format"]

        # The header.
        header: str = (
            "# OpenDX density file written by write_dx()\n"
            f"object 1 class gridpositions counts {resolution}\n"
            f"origin {self.coord[0][0]:6f} {self.coord[0][1]:6f} "
            f"{self.coord[0][2]:6f}\n"
            f"delta  {self.delta[0]:5f} 0 0\n"
            f"delta  0 {self.delta[1]:5f} 0\n"
            f"delta  0 0 {self.delta[2]:5f}\n"
            f"object 2 class gridconnections counts {resolution}\n"
            'object 3 class array type "float" rank 0 items '
            f"{np.prod(self.resolution)} data follows"
        )

        # ======
        # Footer
        # ======

        footer: str = (
            "{}\n"
            'attribute "dep" string "positions"\n'
            'object "density" class field\n'
            'component "positions" value 1\n'
            'component "connections" value 2\n'
            'component "data" value 3'
        )

        for property_i in tqdm(self.__property, desc="COMPUTING PROPERTIES"):
            if self.__argument.verbose:
                print(property_i)

            # Create the grid.
            grid: np.ndarray = np.zeros(self.resolution, dtype=np.half)

            # Compute properties inside the grid.
            property_i.populate_grid(grid=grid, grid_object=self)

            # Trim the grid.
            grid[self.mask] = 0

            path: str = (
                f"{self.__argument.output}/{date}_" f"{property_i.name()}.{format}"
            )

            
            # ============
            # File writing
            # ============
            if self.yaml["other_volume_format"] == "dx":
                self.save_dx(path=path, grid=grid, header=header, footer=footer)
            elif self.yaml["other_volume_format"] == "mrc":
                self.save_mrc(path=path, grid=grid)


    def save_dx(self, grid: np.ndarray, path: str, header: str, footer: str):
        grid_size: int = np.prod(grid.shape)
        n_row: int = grid_size // 3

        # pylint: disable=unbalanced-tuple-unpacking
        # It is balanced, pylint, you know…
        format_grid, extra_line = np.split(grid.flatten(), [3 * n_row])
        # pylint: enable=unbalanced-tuple-unpacking
        format_grid: np.ndarray = format_grid.reshape(n_row, 3)
        extra_line: np.ndarray = extra_line.reshape(1, extra_line.shape[0])

        # Converting the extra line into a string.
        extra_line = " ".join(np.round(extra_line[0], 3).astype(str))

        # ============
        # File writing
        # ============
        with open(path, "wb") as file:
            np.savetxt(
                fname=file,
                X=format_grid,
                fmt="%.3f",
                delimiter=" ",
                header=header,
                footer=footer.format(extra_line),
                comments="",
            )

    
    def save_mrc(self, grid: np.ndarray, path: str):
        data = grid.T
        with mrc.mrcfile.new(path) as mrc_file:
            mrc_file.set_data(data.astype(np.float32)) # mrc is very picky with the allowed data types
            mrc_file.voxel_size = self.delta.tolist()
            mrc_file.header["origin"]['x'] = self.coord[0][0]
            mrc_file.header["origin"]['y'] = self.coord[0][1]
            mrc_file.header["origin"]['z'] = self.coord[0][2]
            mrc_file.update_header_from_data()
            mrc_file.update_header_stats()
