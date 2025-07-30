# 📈 Performance

## Launching `performance_assessor.py`

!!! warning
    In order to launch the script, **YOU HAVE TO** install first `smiffer` as describe in the [installation guide](../installation).

!!! warning
    In order to launch the script, **YOU HAVE TO** install first `perfassess` as describe in this next installation guide: [https://pypi.org/project/perfassess/](<[../installation](https://pypi.org/project/perfassess/)>). But in short, you can do:

    ```sh
    pip install perfassess
    ```

In the root project directory (`📁 smiffer/ `), launch the next command to compute the plots present further in this part:

```sh
python src/misc/performance_assessor.py
```

The next given information is for `6X3V.pdb`, for the `whole` mode.

## 🗂 Function and method architecture

You can scroll through next diagram to see which functions and methods are linked to which, in order to understand next plots.

<div style="background-color: #FFFFFF; overflow: auto; padding: 1cm;">
    <img src="../../ressources/svg/code_architecture.svg" width="2000cm"/>
</div>

## 🧠 Memory evaluation

!!! note
The `x axis` is named like this: `package` + `/file.py` + `:line`.

<div style="background-color: #FFFFFF;">
    <iframe src="../../ressources/plot/memory_evaluation.html"></iframe>
</div>

## ⏳ Time evaluation

!!! note
    The `x axis` is named like this: `file.py` + `:line` + `(function or method)`.

??? note "**Table that describe dropdown values**"
    | **Value** | **Description**                                                                                                       |
    | :-------: | :-------------------------------------------------------------------------------------------------------------------- |
    | `ncalls`  | Shows the number of calls made.                                                                                       |
    | `tottime` | Total time taken by the given function. The time made in calls to sub-functions are excluded.                         |
    | `percall` | Total time per numbers of calls.                                                                                      |
    | `cumtime` | Like `tottime`, but includes time spent in all called subfunctions.                                                     |
    | `percall` | Quotient of `cumtime` divided by primitive calls. The primitive calls include all calls not included through recursion. |

<div style="background-color: #FFFFFF;">
    <iframe src="../../ressources/plot/time_evaluation.html"></iframe>
</div>
