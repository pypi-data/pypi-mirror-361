# 📦 Module

## General note

The script is think to be used as [a command line tool](../command_line). But if you find interesting to use it this way, feel free to. In case of any questions, to not hesitate to open a GitLab issue!

## Importation

### Main module

To import the script, simply do:

```py
import smiffer
```

### Submodule

Access to other class and functions in the submodules like so:

```py
# Access to class
import smiffer.utils as smf_u

smf_u.AtomConstant
```

!!!note
    **You do not need to do something like this:**

    ```py
    from smiffer.utils.class_atom_constant import AtomConstant

    AtomConstant
    ```

    The `__init__.py` files are here to simplify the function / class importation.
