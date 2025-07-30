"""Contains a function to parse given arguments."""

__authors__ = ["Lucas ROUAUD"]
__contact__ = ["lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"

# [O]
from os.path import exists, isdir

# [T]
from textwrap import dedent

# [A]
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter


def parse_argument(version: str = "") -> Namespace:
    """Parse given arguments and tests them.

    Parameters
    ----------
    version : `str`, optional
        The script version. By default None.

    Returns
    -------
    `Namespace`
        The object with parsed arguments.

    Raises
    ------
    FileNotFoundError
        When a file or a directory given in argument does not exist, throw an
        error.

    ValueError
        When a file have a wrong extension or is a not directory, throw an
        error.
    """
    logo: str = """
                 _____                                 _____
                ( ___ )-------------------------------( ___ )
                 |   |                                 |   |
                 |   | ░█▀▀▀░█▄░▄█░▀█▀░█▀▀░█▀▀░█▀▀░█▀▄ |   | 
                 |   | ░▀▀▀█░█░▀░█░░█ ░█▀▀░█▀▀░█▀▀░█▀▄ |   |
                 |   | ░▀▀▀▀░▀  ░▀░▀▀▀░▀  ░▀  ░▀▀▀░▀░▀ |   |
                 |   |                                 |   |
                (_____)-------------------------------(_____)
    """


    print(logo[1:])

    # Description of the program given when the help is cast.
    description: str = """
    Program to compute physical and chemical properties of a protein or a RNA.
    Input take a PDB file and gives fields in OpenDX format. To use the
    program, the simplest command line is:
    
    \033[1m$ smiffer -i 8C3R.pdb -o output/\033[0m 
    
    \033[7m Legend: \033[0m
        - int: Integer.
        - [type|value]: Type of the input required, follow by the default
                        value. So if this optional arguments is not used,
                        "value" will be chosen.
    
    \033[7m Documentation: https://smiffer.mol3d.tech \033[0m
    """
    # ===================
    #
    # ADD ARGUMENT PARSER
    #
    # ===================

    # Setup the arguments parser object.
    parser: Namespace = ArgumentParser(
        description=dedent(description)[1:-1],
        formatter_class=RawTextHelpFormatter,
        add_help=False,
    )

    # == REQUIRED.
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        required=True,
        type=str,
        metavar="[FILE]['.pdb']",
        help='\033[7m [[MANDATORY]] \033[0m\n    > A ".pdb" file.',
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        required=True,
        type=str,
        metavar="[DIRECTORY]",
        help=(
            "\033[7m [[MANDATORY]] \033[0m\n    > A folder where the "
            "results will be stored."
        ),
    )

    # == OPTIONAL.
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="    > Display this help message, then exit the program.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Program version is {version}",
        help="    > Display the program's version, then exit the program.",
    )

    parser.add_argument(
        "-p",
        "--parameter",
        default=None,
        type=str,
        metavar="[FILE|None]['.yml']",
        help=(
            '    > A "YAML" parameter file. If not given, default values\n'
            "      are used."
        ),
    )

    parser.add_argument(
        "-a",
        "--apbs",
        default=None,
        type=str,
        metavar="[FILE|None]['.dx']",
        help=(
            '    > A "OpenDX" file output by APBS. If not given, no APBS\n'
            "      file will be produced."
        ),
    )

    parser.add_argument(
        "--log",
        action="store_true",
        help=(
            "    > When APBS and this flags are given, an additional file\n"
            "      containing LOG of APBS while be computed."
        ),
    )

    parser.add_argument(
        "--verbose",
        required=False,
        action="store_true",
        help=(
            "    > If used, the program give more information on what is\n"
            "      happening."
        ),
    )

    argument = parser.parse_args()

    # ============
    #
    # CHECK ERRORS
    #
    # ============

    # Deleting potential "/" at directory end.
    argument.output = argument.output.rstrip("/")

    __test_parsed_argument(argument=argument)

    return argument


def __test_parsed_argument(argument: Namespace):
    """Test all setup arguments to see if they are correct or not.

    Parameters
    ----------
    argument : `Namespace`
        The parsed arguments.
    """
    # Test argument "--input".
    __test_error(
        argument=argument,
        key="input",
        condition=".pdb",
        message='extension is not ".pdb".',
    )

    # Test argument "--output".
    __test_error(
        argument=argument,
        key="output",
        condition="isdir",
        message='extension is not ".pdb".',
    )

    # Test argument "--parameter".
    __test_error(
        argument=argument,
        key="parameter",
        condition=".yml",
        message='extension is not ".yml".',
        optional=True,
    )

    # Test argument "--apbs".
    __test_error(
        argument=argument,
        key="apbs",
        condition=".dx",
        message='extension is not ".dx".',
        optional=True,
    )

    if argument.log and argument.apbs is None:
        raise ValueError(
            "[Err##] When --log flag is used, --apbs is required."
        )


def __test_error(
    argument: Namespace,
    key: str,
    condition: str,
    message: str,
    optional=False,
):
    """Test potential erros for a given argument.

    Parameters
    ----------
    argument : `Namespace`
        Argument to test.

    key : `str`
        The name of the argument to test.

    condition : `str`
        The condition to test.

    message : `str`
        The error message.

    optional : `bool`, optional
        If it is `True`, check nothing if the argument is `None`. Else, if
        `False`, check the error. By default `False`.

    Returns
    -------
    None

    Raises
    ------
    `FileNotFoundError`
        When the given path is not found.

    `ValueError`
        When the extension is wrong.

    `ValueError`
        When the path is not a directory.
    """
    value: str = getattr(argument, key)

    # Skip if value is None and optional.
    if value is None and optional:
        return None

    # Path not found.
    if not exists(value):
        raise FileNotFoundError(
            f'[Err##] In {key}, "{value}" does not ' "exist."
        )

    if condition == "isdir":
        condition = not isdir(value)
    else:
        condition = not value.endswith(condition)

    # Check the extension or if it is a directory.
    if condition:
        raise ValueError(f"[Err##] In {key}, {message}.")

    return None


if __name__ == "__main__":
    parse_argument()
