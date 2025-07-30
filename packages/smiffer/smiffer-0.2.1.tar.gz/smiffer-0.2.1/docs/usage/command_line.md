# 🚀 Launching the software

## 🎥 Example

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

## 🔍 Describing possible parameters

| **Argument**              | **Mandatory?** | **Type and usage**     | **Description**                                                              |
| :------------------------ | :------------: | :--------------------- | :--------------------------------------------------------------------------- |
| **`-i` or `--input`**     |      Yes       | `--input file.pdb`     | The `.pdb` file that while be used<br/>to computed the properties.           |
| **`-o` or `--output`**    |      Yes       | `--output directory`   | The directory to output the results.                                         |
| **`-p` or `--parameter`** |       No       | `--parameter file.yml` | The YAML parameters file.                                                    |
| **`-a` or `--apbs`**      |       No       | `--apbs file.dx`       | The already computed APBS<br/>electrostatic grid.                            |
| **`-h` or `--help`**      |       No       | Flag                   | Display the help and exit the<br/>program.                                   |
| **`-v` or `--version`**   |       No       | Flag                   | Display the version and exit the<br/>program.                                |
| **`--verbose`**           |       No       | Flag                   | Activated a verbose mode, so more<br/>information are going to be displayed. |
