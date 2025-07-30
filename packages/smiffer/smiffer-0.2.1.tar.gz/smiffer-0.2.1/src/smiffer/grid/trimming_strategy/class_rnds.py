"""Contains a class with strategy to trim a grid based on RNDS."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [N]
import numpy as np

# [C]
from .class_trimming import StrategyTrimming

# pylint: disable=too-few-public-methods
# Trimming class that does not need a lot of method.


class StrategyRndsTrimming(StrategyTrimming):
    """A class to define strategies to trim a grid based on RNDS.

    Inheritance
    -----------
    This class is the child of `StrategyTrimming`. Check this one for other
    **attributes** and **methods** definitions.
    """

    def trim_box(self, grid_object):
        """Trim a grid mask based on RNDS trimming method.

        Parameters
        ----------
        grid_object : `Grid`
            The grid object to access all attributes.
        """
        # Setting max distance RNDS trimming.
        max_dist: float = grid_object.yaml["trimming_distance_rnds_maximum"]

        if max_dist is None:
            max_dist = np.inf

        # Compute all combinaison between [0, 1, -1].
        direction: np.ndarray = np.array(
            np.meshgrid([0, 1, -1], [0, 1, -1], [0, 1, -1])
        ).T.reshape(-1, 3)

        direction = np.delete(direction, [0, 0, 0], axis=0)

        if not grid_object.yaml["other_neighbour_system"]:
            direction = direction[~np.any(np.isin(direction, 0), axis=1)]

        low_mesh: np.ndarray = (
            grid_object.resolution / 2
            - grid_object.yaml["other_cog_cube_radius"]
        )

        high_mesh: np.ndarray = (
            grid_object.resolution / 2
            + grid_object.yaml["other_cog_cube_radius"]
            + 1
        )

        # Compute all combinaison between all coordinates.
        iterator: np.ndarray = (
            np.array(
                np.meshgrid(
                    np.arange(low_mesh[0], high_mesh[0]),
                    np.arange(low_mesh[1], high_mesh[1]),
                    np.arange(low_mesh[2], high_mesh[2]),
                )
            )
            .T.reshape(-1, 3)
            .astype(int)
        )

        # Filling with 0 based on the iterator.
        search_dist: np.ndarray = np.full(grid_object.resolution, np.inf)
        search_dist[tuple(iterator.T)] = 0

        cog_cube: np.ndarray = np.unique(iterator, axis=0)
        # Clean this huge numpy array.
        del iterator

        visited: np.ndarray = np.zeros(grid_object.resolution, dtype=bool)

        # While there is neighbors to visit.
        while cog_cube.shape[0] != 0:
            node = cog_cube[0]

            # Deleting the first items in cog_cub np.array.
            cog_cube = cog_cube[1:]

            visited[tuple(node)] = True

            neighbour = direction + node

            # Masking data that are not included between 0 and resolution.
            mask: np.ndarray = np.all(
                (np.array([0, 0, 0]) <= neighbour)
                & (neighbour < grid_object.resolution),
                axis=1,
            )

            # Filter neighbors.
            neighbour: tuple = tuple(neighbour[mask].T)

            search_dist[neighbour] = np.min(
                (
                    [search_dist[tuple(node)] + 1]
                    * search_dist[neighbour].shape[0],
                    search_dist[neighbour],
                ),
                axis=0,
            )

            # Skipping data not responding to these criteria:
            # 1. Checking that every value are strictly greater than
            #    self.max_dist, else skip.
            # 2. Checking that value have not been visited.
            # 3. Checking that the mask value are set to False.
            #
            # If any of this criteria are not respected, the return value is
            # False, so it is not added into the cog_cube np.array.
            mask: np.ndarray = (
                (search_dist[neighbour] > max_dist)
                | visited[neighbour]
                | grid_object.mask[neighbour]
            )

            # Appending selected data.
            cog_cube = np.vstack((cog_cube, np.array(neighbour).T[~mask]))
            visited[tuple(np.array(neighbour).T[~mask].T)] = True

        # Masking data.
        grid_object.mask[~visited] = True


# pylint: enable=too-few-public-methods
