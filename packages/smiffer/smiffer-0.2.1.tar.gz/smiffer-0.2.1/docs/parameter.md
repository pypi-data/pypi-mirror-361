# 🪛 Parameters file ⚙️

Here are list all available parameters for a `parameter_file.yml`!

!!! note "Complete example file"
    You can found the most complete example file here:
    [https://gitlab.galaxy.ibpc.fr/rouaud/smiffer/-/blob/main/data/default_parameter.yml](https://gitlab.galaxy.ibpc.fr/rouaud/smiffer/-/blob/main/data/default_parameter.yml)

!!! note
    All displayed values are the default ones if none are given.

## Box/Grid parameters

!!! note
    Box and grid are equivalent terms, here.

### Delta

```yaml
box:
    delta:
        x: 0.25
        y: 0.25
        z: 0.25
```

**Positive float values.** Use either these or resolution, but not both. Step
between each point of the grid. Note that, from the delta, the resolution will
be obtained as so:

$$
delta = \dfrac{box~size}{resolution}
$$

### Resolution

```yaml
box:
    resolution:
        x: 100
        y: 100
        z: 100
```

**Positive int values.** Use either these or delta, but not both. Number of points into the grid. Not that, from the resolution, the delta will be obtained as so:

$$
resolution = round\_to\_integer\left( \dfrac{box~size}{delta} \right)
$$

### Box extra size

```yaml
box:
    extra_size: 5
```

**Positive int value.** Add, when being in “whole” mode, a extra size arround the grid.

### Area mode

```yaml
box:
    area_mode: whole
```

**String value between whole or pocket_sphere**. If “whole” is choosen, the whole protein or RNA is taken to compute fields. Else, only a selected area is choosen.

### Box center

```yaml
box:
    center:
        x: 0
        y: 0
        z: 0
```

**Float values.** Were to put the center of the box. Used only in “pocket sphere” mode. _See next part for a 2D representation scheme._

### Radius

```yaml
box:
    radius: 10
```

**Positive integer value.** The “radius” of the box. Used only in “pocket_sphere” mode. It is used to compute the box size. Scheme of the box/grid:

<pre><code style="line-height: 1.18;">
┏━━━━━━━━━━━┓
┃     center┃
┃     ↓     ┃
┃-----x     ┃
┃  ↑        ┃
┃  radius   ┃
┗━━━━━━━━━━━┛
├───────────┤
  box  size
</code></pre>

## Trimming parameter

### Enable sphere trimming

```yaml
trimming:
    sphere: false
```

**Boolean value.** `True` to trim compute fields in a round shape arround the protein or RNA.

### Enable trimming occupancy

```yaml
trimming:
    occupancy: true
```

**Boolean value.** `True` to trim fields in function of occupancy. If a atom of the protein or RNA is overlap with the field, it will remove the field in this area.

### Enable RNDS trimming

```yaml
trimming:
    rnds: false
```

**Boolean value.** `True` to trim using a fill algorithm, it select all connected area delete all other unconnected one. For people that use tools like GIMP or Photoshop, it would be doing something like: magic wand selection > invert selection > delete.

### Occupancy trimming enlargement

```yaml
trimming:
    distance:
        atom_minimum: 3.0
```

**Positive float value.** Enlarge the area around the select protein or RNA in order to enhance a little more the occupancy trimming.

### RNDS maximum distance trimming

```yaml
trimming:
    distance:
        rnds_maximum: none
```

**None or positive float value.** Limit the RNDS trimming distance.

## Special APBS parameter

### Log APBS cut-off

```yaml
apbs:
    cut_off: [-2.0, 3.0]
```

## Statistical parameter

### H-bond &micro; statistical parameter

```yaml
statistical_energy_function:
    h_bond:
        mu: 3.0
```

**Float value.** Statistical &micro; parameter for the gaussian function.

### H-bond &sigma; statistical parameter

```yaml
statistical_energy_function:
    h_bond:
        sigma: 0.15
```

**Float value.** Statistical &sigma; parameter for the gaussian function.

### Hydrophobic &micro; statistical parameter

```yaml
statistical_energy_function:
    hydrophobic:
        mu: 4.0
```

**Float value.** Statistical &micro; parameter for the gaussian function.

### Hydrophobic &sigma; statistical parameter

```yaml
statistical_energy_function:
    hydrophobic:
        sigma: 1.5
```

**Float value.** Statistical &sigma; parameter for the gaussian function.

### Hydrophilic &micro; statistical parameter

```yaml
statistical_energy_function:
    hydrophilic:
        mu: 3.0
```

**Float value.** Statistical &micro; parameter for the gaussian function.

### Hydrophilic &sigma; statistical parameter

```yaml
statistical_energy_function:
    hydrophilic:
        sigma: 0.15
```

**Float value.** Statistical &sigma; parameter for the gaussian function.

### Pi stacking &micro; statistical parameter

```yaml
statistical_energy_function:
    pi_stacking:
        mu: [29.98, 4.188]
```

**Float value.** Statistical &micro; parameter for the gaussian function.

### Pi stacking &sigma; statistical parameter

```yaml
statistical_energy_function:
    pi_stacking:
        sigma: [[169.99, 6.6232], [6.6232, 0.37124]]
```

**Float value.** Statistical &sigma; parameter for the gaussian function.

## Unclassified parameters

### Gaussian kernel size scalar

```yaml
other:
    gaussian_kernel_scalar: 4.0
```

**Positive float value.** Increase by this value the size of the Gaussian kernel. It is compute as follow:

$$
kernel~radius = \mu_{factor} + \sigma_{factor} \times gaussian\_kernel\_scalar
$$

### RNDS neighbour system

```yaml
other:
    neighbour_system: true
```

**Boolean value.** `True`, do only check for next iteration corners. Basically, it changes the way of visiting neighbour point while doing the RNDS trimming method.

???info "Illustration of this parameter functioning"
    Let us say we are in a 2D space. We start from point (0, 0). From this point, we can visit these next ones:

    (0, 1), (1, 0), (1, 1), (-1, -1), (-1, 0), (0, -1), (-1, 1), (1, -1)

    In other words, we could say that we can go up, down, left, right and the corners (top right, etc.). By setting this option to `True`, we only visite the corners, so these points:

    (1, 1), (-1, -1), (1, -1), (-1, 1)

### Cog cube radius

```yaml
other:
    cog_cube_radius: 3.0
```

**Positive float.** Help to precompute a set of coordinates to visite for the RNDS trimming.

### Type of macromolecule

```yaml
other:
    macromolecule: protein
```

**String value between protein or nucleic.** Select a type of macromolecule depending of the given parameters.

## Properties to compute

### H-bond donor

```yaml
flag:
    h_bond_donor: true
```

**Boolean value.** `True` to enable the computation of H-bond donor fields.

### H-bond acceptor flag

```yaml
flag:
    h_bond_acceptor: true
```

**Boolean value.** `True` to enable the computation of H-bond acceptor fields.

### Hydrophobic flag

```yaml
flag:
    hydrophobic: true
```

**Boolean value.** `True` to enable the computation of hydrophobic fields.

### Hydrophilic flag

```yaml
flag:
    hydrophilic: true
```

**Boolean value.** `True` to enable the computation of hydrophilic fields.

### Pi stacking flag

```yaml
flag:
    pi_stacking: true
```

**Boolean value.** `True` to enable the computation of pi stacking fields.
