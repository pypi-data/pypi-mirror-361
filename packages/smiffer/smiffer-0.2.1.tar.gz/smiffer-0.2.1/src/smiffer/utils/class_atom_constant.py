"""Contains a class in order to parse a `.yaml` parameter file."""

__authors__ = ["Diego BARQUERO MORERA", "Lucas ROUAUD"]
__contact__ = ["diegobarqueromorera@gmail.com", "lucas.rouaud@gmail.com"]
__copyright__ = "MIT License"


class AtomConstant:
    """Define atoms constants.

    Attributes
    ----------
    self.__AROMATIC : `dict`
        A dictionary mapping atom implied in cycle, for given residue.

    self.__WW_SCALE : `dict`
        A dictionary with the different residue WW values.

    self.__BACKBONE_PHOSPHATE : `list`
        List of nucleic acid phosphate atoms.

    self.__BACKBONE_SUGAR : `list`
        List of nucleic acid sugar atoms.

    self.__NUCLEIC_BASES : `dict`
        List of nucleic acid bases atoms.

    self.__HPHIL_RNA_SUGAR : `float`
        Hydrophilic value for nucleic acid sugar atoms.
    
    self.__HPHIL_RNA_PHOSPHATE : `float`
        Hydrophilic value for nucleic acid phosphate atoms.

    self.__H_B_ACCEPTOR : `dict`
        A dictionary mapping atom implied in hydrogen bond acceptor, for given
        residue.

    self.__H_B_DONOR : `dict`
        A dictionary mapping atom implied in hydrogen bond donor, for given
        residue.

    self.__KEY : `list`
        A list of available keys.

    self.__VALUE : `list`
        A list containing all available dictionnaries.
    """

    # List of atoms implied in cycle, taking in consideration residues
    # and RNA bases.
    __AROMATIC: dict = {
        "HIS": "CD2 CE1 CG ND1 NE2",
        "PHE": "CD1 CD2 CE1 CE2 CG CZ",
        "TRP": "CD1 CD2 CE2 CE3 CG CH2 CZ2 CZ3 NE1",
        "TYR": "CD1 CD2 CE1 CE2 CG CZ",
        "U": "N1 C2 N3 C4 C5 C6",
        "C": "N1 C2 N3 C4 C5 C6",
        "A": "N1 C2 N3 C4 C5 C6 N7 C8 N9",
        "G": "N1 C2 N3 C4 C5 C6 N7 C8 N9",
    }

    # List of side chain hydrophobicity scores, from Wimley and White Scale.
    # Values for RNA bases are taken from analogous protein residues.
    __WW_SCALE: dict = {
        "ALA" : -0.17,
        "ARG" : -0.81,
        "ASN" : -0.42,
        "ASP" : -1.23,
        "CYS" :  0.24,
        "GLN" : -0.58,
        "GLU" : -2.02,
        "GLY" : -0.01,
        "HIS" : -0.96,
        "ILE" :  0.31,
        "LEU" :  0.56,
        "LYS" : -0.99,
        "MET" :  0.23,
        "PHE" :  1.13,
        "PRO" : -0.45,
        "SER" : -0.13,
        "THR" : -0.14,
        "TRP" :  1.85,
        "TYR" :  0.94,
        "VAL" : -0.07,
        "U"   :  1.13,
        "C"   :  1.13,
        "A"   :  1.85,
        "G"   :  1.85,
    }

    __BACKBONE_PHOSPHATE = ["O5'", "P", "OP1", "OP2", "O3'"]

    __BACKBONE_SUGAR = ["C1'", "C2'", "C3'", "C4'", "C5'", "O2'", "O4'"]

    __NUCLEIC_BASES = {
        "U" : ["N1", "C2", "N3", "C4", "C5", "C6", "O2", "O4"],
        "C" : ["N1", "C2", "N3", "C4", "C5", "C6", "O2", "N4"],
        "A" : ["N1", "C2", "N3", "C4", "C5", "C6", "N7", "C8", "N9", "N6"],
        "G" : ["N1", "C2", "N3", "C4", "C5", "C6", "N7", "C8", "N9", "N2", "O6"],
    }

    __HPHIL_RNA_SUGAR = -0.13

    __HPHIL_RNA_PHOSPHATE = -2.02

    # List of atoms implied in hydrogen bond acceptor, taking in consideration
    # residues and RNA bases.
    __H_B_ACCEPTOR: dict = {
        "ALA": [
            [("C",), "O"]
        ],
        "ARG": [
            [("C",), "O"],
        ],
        "ASN": [
            [("C",), "O"],
            [("CG",), "OD1"]
        ],
        "ASP": [
            [("C",), "O"],
            [("CG",), "OD1"],
            [("CG",), "OD2"]
        ],
        "CYS": [
            [("C",), "O"],
            [("CB",), "SG"]
        ],
        "GLU": [
            [("C",), "O"],
            [("CD",), "OE1"],
            [("CD",), "OE2"]
        ],
        "GLN": [
            [("C",), "O"],
            [("CD",), "OE1"]
        ],
        "GLY": [
            [("C",), "O"]
        ],
        "HIS": [
            [("C",), "O"],
            [("CE1", "CG",), "ND1"], # pseudo-antecedent
        ],
        "ILE": [
            [("C",), "O"]
        ],
        "LEU": [
            [("C",), "O"]
        ],
        "LYS": [
            [("C",), "O"],
        ],
        "MET": [
            [("C",), "O"],
            [("CG",), "SD"]
        ],
        "PHE": [
            [("C",), "O"]
        ],
        "PRO": [
            [("C",), "O"]
        ],
        "SER": [
            [("C",), "O"],
            [("CB",), "OG"]
        ],
        "THR": [
            [("C",), "O"],
            [("CB",), "OG1"]
        ],
        "TRP": [
            [("C",), "O"],
        ],
        "TYR": [
            [("C",), "O"],
            [("CZ",), "OH"]
        ],
        "VAL": [
            [("C",), "O"]
        ],
        "U": [
            [("C2'",), "O2'"],
            [("C3'", "P",), "O3'"], # pseudo-antecedent (special case)
            [("C1'", "C4'",), "O4'"], # pseudo-antecedent
            [("C5'", "P",), "O5'"], # pseudo-antecedent
            [("P",), "OP1"],
            [("P",), "OP2"],
            [("C2",), "O2"],
            [("C4",), "O4"]
        ],
        "C": [
            [("C2'",), "O2'"],
            [("C3'", "P",), "O3'"], # pseudo-antecedent (special case)
            [("C1'", "C4'",), "O4'"], # pseudo-antecedent
            [("C5'", "P",), "O5'"], # pseudo-antecedent
            [("P",), "OP1"],
            [("P",), "OP2"],
            [("C2",), "O2"],
            [("C2", "C4",), "N3"], # pseudo-antecedent
        ],
        "A": [
            [("C2'",), "O2'"],
            [("C3'", "P",), "O3'"], # pseudo-antecedent (special case)
            [("C1'", "C4'",), "O4'"], # pseudo-antecedent
            [("C5'", "P",), "O5'"], # pseudo-antecedent
            [("P",), "OP1"],
            [("P",), "OP2"],
            [("C2", "C6",), "N1"], # pseudo-antecedent
            [("C2", "C4",), "N3"], # pseudo-antecedent
            [("C5", "C8",), "N7"], # pseudo-antecedent
        ],
        "G": [
            [("C2'",), "O2'"],
            [("C3'", "P",), "O3'"], # pseudo-antecedent (special case)
            [("C1'", "C4'",), "O4'"], # pseudo-antecedent
            [("C5'", "P",), "O5'"], # pseudo-antecedent
            [("P",), "OP1"],
            [("P",), "OP2"],
            [("C2", "C4",), "N3"], # pseudo-antecedent
            [("C5", "C8",), "N7"], # pseudo-antecedent
            [("C6",), "O6"]
        ]
    }

    # List of atoms implied in hydrogen bond donor, taking in consideration
    # residues and RNA bases.
    __H_B_DONOR: dict = {
        "ALA": [
            [("CA",), "N"]
        ],
        "ARG": [
            [("CA",), "N"],
            [("CD", "CZ",), "NE"], # pseudo-antecedent
            [("CZ",), "NH1"],
            [("CZ",), "NH2"]
        ],
        "ASN": [
            [("CA",), "N"],
            [("CG",), "ND2"]
        ],
        "ASP": [
            [("CA",), "N"]
        ],
        "CYS": [
            [("CA",), "N"],
            [("CB",), "SG"]
        ],
        "GLU": [
            [("CA",), "N"]
        ],
        "GLN": [
            [("CA",), "N"],
            [("CD",), "NE2"]
        ],
        "GLY": [
            [("CA",), "N"]
        ],
        "HIS": [
            [("CA",), "N"],
            [("CD2", "CE1",), "NE2"] # pseudo-antecedent
        ],
        "ILE": [
            [("CA",), "N"]
        ],
        "LEU": [
            [("CA",), "N"]
        ],
        "LYS": [
            [("CA",), "N"],
            [("CE",), "NZ"]
        ],
        "MET": [
            [("CA",), "N"]
        ],
        "PHE": [
            [("CA",), "N"]
        ],
        "PRO": [],
        "SER": [
            [("CA",), "N"],
            [("CB",), "OG"]
        ],
        "THR": [
            [("CA",), "N"],
            [("CB",), "OG1"]
        ],
        "TRP": [
            [("CA",), "N"],
            [("CD1", "CE2",), "NE1"] # pseudo-antecedent
        ],
        "TYR": [
            [("CA",), "N"],
            [("CZ",), "OH"]
        ],
        "VAL": [
            [("CA",), "N"]
        ],
        "U": [
            [("C2'",), "O2'"],
            [("C3'",), "O3'"], # (special case)
            [("C5'",), "O5'"], # (special case)
            [("C2", "C4",), "N3"] # pseudo-antecedent
        ],
        "C": [
            [("C2'",), "O2'"],
            [("C3'",), "O3'"], # (special case)
            [("C5'",), "O5'"], # (special case)
            [("C4",), "N4"]
        ],
        "A": [
            [("C2'",), "O2'"],
            [("C3'",), "O3'"], # (special case)
            [("C5'",), "O5'"], # (special case)
            [("C6",), "N6"]
        ],
        "G": [
            [("C2'",), "O2'"],
            [("C3'",), "O3'"], # (special case)
            [("C5'",), "O5'"], # (special case)
            [("C2", "C6",), "N1"], # pseudo-antecedent
            [("C2",), "N2"]
        ]
    }

    __KEY: list = [
        "aromatic", "ww_scale", "backbone_phosphate", "backbone_sugar", 
        "nucleic_bases", "hphil_rna_sugar", "hphil_rna_phosphate",
        "h_b_acceptor", "h_b_donor"
    ]
    __VALUE: list = [
        __AROMATIC, __WW_SCALE, __BACKBONE_PHOSPHATE, __BACKBONE_SUGAR, 
        __NUCLEIC_BASES, __HPHIL_RNA_SUGAR, __HPHIL_RNA_PHOSPHATE,
        __H_B_ACCEPTOR, __H_B_DONOR
    ]

    def __setitem__(self, key: str, dictionary: dict):
        """Throws an exception if an setting is tried.

        Parameters
        ----------
        key : `str`
            The key to assign a parameter.

        dictionary : `dict`
            The dictionary to asign.

        Raises
        ------
        TypeError
            Throw when this method is called. Because it has to be not used.
        """
        raise TypeError(
            "[Err##] You cannot modify any attributes in this class!"
        )

    def __getitem__(self, key: str) -> dict:
        """Return a dictionary value corresponding to a given key.

        Parameters
        ----------
        key : `str`
            The key to fetch a dictionary.

        Returns
        -------
        `dict`
            The fetched dictionary.
        """
        if key not in self.__KEY:
            raise ValueError(
                f'[Err##] Key "{key}" not accepted. List of '
                f'accepted keys are "{self.__KEY}".'
            )

        return self.__VALUE[self.__KEY.index(key)]

    def keys(self) -> list:
        """Return keys linked to this object.

        Returns
        -------
        `list`
            The keys.
        """
        return self.__KEY

    def values(self) -> list:
        """Return dictionaries linked to this object.

        Returns
        -------
        `list`
            The values.
        """
        return self.__VALUE

    def items(self) -> zip:
        """Return keys, paired to their dictionaries, linked to this object.

        Returns
        -------
        `zip`
            The pairs key/value.
        """
        return zip(self.__KEY, self.__VALUE)

    def __str__(self) -> str:
        """Redefine the print() function for this object.

        Returns
        -------
        `str`
            The string representation of this object.
        """
        to_print: str = f"Available properties are: {self.__KEY}."

        return to_print


if __name__ == "__main__":
    atom_constant = AtomConstant()

    print(f"atom_constant[aromatic] return:\n {atom_constant['aromatic']}\n")
    print(atom_constant)
