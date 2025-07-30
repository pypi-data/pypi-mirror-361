<div align="center">

# ⌛️ smiffer 🦙

[![Python 3.5](https://img.shields.io/badge/python-%E2%89%A5_3.5.0-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img src="https://smiffer.mol3d.tech/ressources/img/logo_compress.png" width="40%">

Contributors: **Diego BARQUERO MORERA** and **Lucas ROUAUD**

**Documentation:** https://smiffer.mol3d.tech/

</div align="center">

This software is coded in python. It permits to produced grids, into a OpenDX format (`.dx`). With those grids, it is possible to visualize multiple physical and chemical properties around a protein. This permit to see all possible area of interaction (with proteins, ligands or lipids) around a protein.

## ⚙️ Installation

### 📦 Using pipx (recommended)

- pipx link: [https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx](https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx)

```bash
$ pipx install smiffer

# Checking the installation is done.
$ smiffer --help
```

> **🦊 From the GitLab repository:**
> 
> ```bash
> $ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
> $ cd smiffer/
> $ pipx install .
> 
> # Checking the installation is done.
> $ smiffer --help
> ```

### 🐍 Using pip

```bash
$ python3 -m pip install smiffer

# Checking the installation is done.
$ smiffer --help
```

> **🦊 From the GitLab repository:**
> 
> ```bash
> $ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
> $ cd smiffer/
> $ python3 -m pip install .
> 
> # Checking the installation is done.
> $ smiffer --help
> ```

### 🐋 Using docker

```bash
$ 
```

### 🛠 From scratch (not recommended)

```bash
$ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
$ cd smiffer

# Install globaly these packages…
$ pip install -r env/requirements.txt

# Checking the installation is done.
$ python -m src.smiffer --help
```

## 🌐 External software

The APBS server can be found at next url: https://server.poissonboltzmann.org/.

## 🚀 Launching the software

### 🎥 Example

To test the program, use the following commands in `📁 smiffer/`:

```sh
$ mkdir data/output/

# Launching the software.
$ smiffer -i data1EHE.pdb \
$         -p data1EHE_parameter.yml \
$         -a data/1EHE_APBS.dx \
$         -o data/output/

# Visualize using VMD (or other like PyMol, Chimera, Mol*, etc.).
$ vmd data/1EHE.pdb data/output/*.dx
```

### 🔍 Parameters description

| **Argument**              | **Mandatory?** | **Type and usage**     | **Description**                                                              |
| :------------------------ | :------------: | :--------------------- | :--------------------------------------------------------------------------- |
| **`-i` or `--input`**     |      Yes       | `--input file.pdb`     | The `.pdb` file that while be used<br/>to computed the properties.           |
| **`-o` or `--output`**    |      Yes       | `--output directory`   | The directory to output the results.                                         |
| **`-p` or `--parameter`** |       No       | `--parameter file.yml` | The YAML parameters file.                                                    |
| **`-a` or `--apbs`**      |       No       | `--apbs file.dx`       | The already computed APBS<br/>electrostatic grid.                            |
| **`-h` or `--help`**      |       No       | Flag                   | Display the help and exit the<br/>program.                                   |
| **`-v` or `--version`**   |       No       | Flag                   | Display the version and exit the<br/>program.                                |
| **`--verbose`**           |       No       | Flag                   | Activated a verbose mode, so more<br/>information are going to be displayed. |

## 🙇‍♂️ Acknowledgement

🔍 Code reviewing: **Hubert SANTUZ**

✒️ Formula checking: **Jules MARIEN**

_This work is licensed under a [MIT License](https://opensource.org/licenses/MIT)._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
