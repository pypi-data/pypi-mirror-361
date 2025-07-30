"""Function with all parameters set to check into the ".yaml" parameter file."""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [S]
from .class_set_parameter import SetParameter

# [Y]
from .class_parse_yaml import ParseYaml


def parse_yaml(file_path: str, verbose: bool = False) -> ParseYaml:
    """Set all parameters to check into the ".yaml" parameter file.

    Parameters
    ----------
    file_path : `str`
        The path to the ".yaml" parameter file to parse.

    verbose : `bool`, optional
        Enable verbose mode if `True`. By default `False`, so no verbose.

    Returns
    -------
    `ParseYaml`
        The set ParseYaml object.
    """
    yaml_parser = ParseYaml(file_path, verbose)

    # ==============
    #
    # BOX PARAMETERS
    #
    # ==============
    default_delta: float = 0.25

    yaml_parser["box_delta_x"] = SetParameter(
        default_value=default_delta,
        typing=(int, float, type(None)),
        path="box:delta:x",
        category="Box parameters",
        error={"inferior": 0},
    )

    yaml_parser["box_delta_y"] = SetParameter(
        default_value=default_delta,
        typing=(int, float, type(None)),
        path="box:delta:y",
        category="Box parameters",
        error={"inferior": 0},
    )

    yaml_parser["box_delta_z"] = SetParameter(
        default_value=default_delta,
        typing=(int, float, type(None)),
        path="box:delta:z",
        category="Box parameters",
        error={"inferior": 0},
    )

    delta_is_none: bool = (
        yaml_parser["box_delta_x"]
        and yaml_parser["box_delta_y"]
        and yaml_parser["box_delta_z"]
    ) is None

    default_resolution: int = None

    if delta_is_none:
        default_resolution = 100

        if verbose:
            print(

                'Due to unset "x", "y" or "z" resolution or deltas, '
                "falling back to default behavior by setting resolution to "
                '"100".'
            )

    yaml_parser["box_resolution_x"] = SetParameter(
        default_value=default_resolution,
        typing=(int, type(None)),
        path="box:resolution:x",
        category="Box parameters",
        error={"inferior": 0},
    )

    yaml_parser["box_resolution_y"] = SetParameter(
        default_value=default_resolution,
        typing=(int, type(None)),
        path="box:resolution:y",
        category="Box parameters",
        error={"inferior": 0},
    )

    yaml_parser["box_resolution_z"] = SetParameter(
        default_value=default_resolution,
        typing=(int, type(None)),
        path="box:resolution:z",
        category="Box parameters",
        error={"inferior": 0},
    )

    resolution_is_none: bool = (
        yaml_parser["box_resolution_x"]
        and yaml_parser["box_resolution_y"]
        and yaml_parser["box_resolution_z"]
    ) is None

    if not delta_is_none and not resolution_is_none:
        raise ValueError(
            "[Err##] You can only set either resolution or deltas"
            ", but not both."
        )

    yaml_parser["box_extra_size"] = SetParameter(
        default_value=5,
        typing=(int, float),
        path="box:extra_size",
        category="Box parameters",
        error={"inferior": 0},
    )

    yaml_parser["box_area_mode"] = SetParameter(
        default_value="whole",
        typing=str,
        path="box:area_mode",
        category="Box parameters",
        error={"set": ["whole", "pocket_sphere"]},
    )

    yaml_parser["box_center_x"] = SetParameter(
        default_value=0,
        typing=(int, float),
        path="box:center:x",
        category="Box parameters",
    )

    yaml_parser["box_center_y"] = SetParameter(
        default_value=0,
        typing=(int, float),
        path="box:center:y",
        category="Box parameters",
    )

    yaml_parser["box_center_z"] = SetParameter(
        default_value=0,
        typing=(int, float),
        path="box:center:z",
        category="Box parameters",
    )

    yaml_parser["box_radius"] = SetParameter(
        default_value=10,
        typing=(int, float),
        path="box:radius",
        category="Box parameters",
        error={"inferior": 0},
    )

    # ===================
    #
    # TRIMMING PARAMETERS
    #
    # ===================
    yaml_parser["trimming_sphere"] = SetParameter(
        default_value=False,
        typing=bool,
        path="trimming:sphere",
        category="Trimming parameters",
    )

    yaml_parser["trimming_occupancy"] = SetParameter(
        default_value=True,
        typing=bool,
        path="trimming:occupancy",
        category="Trimming parameters",
    )

    yaml_parser["trimming_rnds"] = SetParameter(
        default_value=False,
        typing=bool,
        path="trimming:rnds",
        category="Trimming parameters",
    )

    yaml_parser["trimming_distance_atom_minimum"] = SetParameter(
        default_value=3.0,
        typing=(int, float),
        path="trimming:distance:atom_minimum",
        category="Trimming parameters",
        error={"inferior": 0},
    )

    yaml_parser["trimming_distance_rnds_maximum"] = SetParameter(
        default_value=None,
        typing=(int, float, type(None)),
        path="trimming:distance:rnds_maximum",
        category="Trimming parameters",
        error={"inferior": 0},
    )

    # ===============
    #
    # APBS PARAMETERS
    #
    # ===============
    yaml_parser["apbs_cut_off"] = SetParameter(
        default_value=[-2.0, 3.0],
        typing=[(int, float), (int, float)],
        path="apbs:cut_off",
        category="APBS parameters",
        error={"length": True},
    )

    # ======================================
    #
    # STATISTICAL ENERGY FUNCTION PARAMETERS
    #
    # ======================================
    yaml_parser["function_h_bond_acceptor_mu"] = SetParameter(
        default_value=[129.9, 2.93],
        typing=[(int, float), (int, float)],
        path="statistical_energy_function:h_bond_acceptor:mu",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    yaml_parser["function_h_bond_acceptor_sigma"] = SetParameter(
        default_value=[[400.0, 0.0], [0.0, 0.0441]],
        typing=[[(int, float), (int, float)], [(int, float), (int, float)]],
        path="statistical_energy_function:h_bond_acceptor:sigma",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    yaml_parser["function_h_bond_donor_mu"] = SetParameter(
        default_value=[109.9, 2.93],
        typing=[(int, float), (int, float)],
        path="statistical_energy_function:h_bond_donor:mu",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    yaml_parser["function_h_bond_donor_sigma"] = SetParameter(
        default_value=[[400.0, 0.0], [0.0, 0.0441]],
        typing=[[(int, float), (int, float)], [(int, float), (int, float)]],
        path="statistical_energy_function:h_bond_donor:sigma",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    yaml_parser["function_hydrophobic_mu"] = SetParameter(
        default_value=4.0,
        typing=(int, float),
        path="statistical_energy_function:hydrophobic:mu",
        category="Statistical energy function parameters",
    )

    yaml_parser["function_hydrophobic_sigma"] = SetParameter(
        default_value=1.5,
        typing=(int, float),
        path="statistical_energy_function:hydrophobic:sigma",
        category="Statistical energy function parameters",
    )

    yaml_parser["function_hydrophilic_mu"] = SetParameter(
        default_value=3.0,
        typing=(int, float),
        path="statistical_energy_function:hydrophilic:mu",
        category="Statistical energy function parameters",
    )

    yaml_parser["function_hydrophilic_sigma"] = SetParameter(
        default_value=0.15,
        typing=(int, float),
        path="statistical_energy_function:hydrophilic:sigma",
        category="Statistical energy function parameters",
    )

    yaml_parser["function_pi_stacking_mu"] = SetParameter(
        default_value=[29.98, 4.188],
        typing=[(int, float), (int, float)],
        path="statistical_energy_function:pi_stacking:mu",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    yaml_parser["function_pi_stacking_sigma"] = SetParameter(
        default_value=[[169.99, 6.6232], [6.6232, 0.37124]],
        typing=[[(int, float), (int, float)], [(int, float), (int, float)]],
        path="statistical_energy_function:pi_stacking:sigma",
        category="Statistical energy function parameters",
        error={"length": True},
    )

    # ================
    #
    # OTHER PARAMETERS
    #
    # ================
    yaml_parser["other_gaussian_kernel_scalar"] = SetParameter(
        default_value=4.0,
        typing=(int, float),
        path="other:gaussian_kernel_scalar",
        category="Other parameters",
        error={"inferior": 0},
    )

    yaml_parser["other_neighbour_system"] = SetParameter(
        default_value=True,
        typing=bool,
        path="other:neighbour_system",
        category="Other parameters",
    )

    yaml_parser["other_cog_cube_radius"] = SetParameter(
        default_value=3.0,
        typing=(int, float),
        path="other:cog_cube_radius",
        category="Other parameters",
        error={"inferior": 0},
    )

    yaml_parser["other_macromolecule"] = SetParameter(
        default_value="protein",
        typing=str,
        path="other:macromolecule",
        category="Other parameters",
        error={"set": ["protein", "nucleic"]},
    )

    yaml_parser["other_volume_format"] = SetParameter(
        default_value="dx",
        typing=str,
        path="other:volume_format",
        category="Other parameters",
        error={"set": ["dx", "mrc"]},
    )

    # ===============
    #
    # FLAG PARAMETERS
    #
    # ===============
    yaml_parser["flag_h_bond_donor"] = SetParameter(
        default_value=True,
        typing=bool,
        path="flag:h_bond_donor",
        category="Flags",
    )

    yaml_parser["flag_h_bond_acceptor"] = SetParameter(
        default_value=True,
        typing=bool,
        path="flag:h_bond_acceptor",
        category="Flags",
    )

    yaml_parser["flag_hydrophobic"] = SetParameter(
        default_value=True,
        typing=bool,
        path="flag:hydrophobic",
        category="Flags",
    )

    yaml_parser["flag_hydrophilic"] = SetParameter(
        default_value=True,
        typing=bool,
        path="flag:hydrophilic",
        category="Flags",
    )

    yaml_parser["flag_pi_stacking"] = SetParameter(
        default_value=True,
        typing=bool,
        path="flag:pi_stacking",
        category="Flags",
    )

    return yaml_parser


if __name__ == "__main__":
    print(parse_yaml("default_parameters.yml", False))
