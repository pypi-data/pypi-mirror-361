# class_pi_stacking.py

Computation is based on next formula:

$$
    \phi_{\pi \text{ st}} = -\displaystyle\sum_{r = 1}^R \exp\left[-\dfrac{(\pmb{v}_r - \pmb{\mu}_{\pi \text{ st}})^T \pmb{S}_{\pi \text{ st}}^{-1} (\pmb{v}_r - \pmb{\mu}_{\pi \text{ st}})}{2} \right]
$$

With \(\phi_{\pi \text{ st}}\) the field in a 3D space, \(R\) the selected ring, and where: 

$$
    \pmb{v}_r = \begin{bmatrix} \alpha_r \\ d_r \end{bmatrix} \quad \& \quad
    \pmb{\mu}_{\pi \text{ st}} = \begin{bmatrix} \alpha_0 \\ d_0 \end{bmatrix}
                               = \begin{bmatrix} 29.98~^\circ \\ 4.19~\text{Å} \end{bmatrix}
$$

$$
    \& \quad \pmb{S}_{\pi \text{ st}} = \begin{bmatrix} \sigma^2 \left(\alpha \right) & \sigma \left( \alpha, d \right) \\ \sigma \left( d, \alpha \right) & \sigma^2 \left( d \right) \end{bmatrix}
                             = \begin{bmatrix} 169.99~(^\circ)^2 & 6.62~^\circ \cdot \text{Å} \\ 6.62~^\circ \cdot \text{Å} & 0.37~\text{Å}^2 \end{bmatrix}
$$

With \(\pmb{v}_r\) the matrix with the actual computed distance _(any position to the ring center of geometry)_ and angle _(between the normal vector of the ring plan and a vector from the ring center of geometry to any position)_, \(\pmb{\mu}_{\pi \text{ st}}\) the optimal distance and angle, \(\pmb{S}_{\pi \text{ st}}\) a matrix with variances.
 
::: src.smiffer.grid.property_strategy.class_pi_stacking
