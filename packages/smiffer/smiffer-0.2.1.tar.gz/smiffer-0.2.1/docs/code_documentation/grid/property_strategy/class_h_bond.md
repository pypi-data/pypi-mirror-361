# class_h_bond.py

Computation is based on next formula:

$$
\phi_{\text{h-b}} = - \displaystyle\sum_{a=1}^{A} \exp \left[ - \dfrac{\left( \mu_{\text{h-b}} - d_a \right)^2}{2 \sigma_{\text{h-b}}^2} \right]
$$

With \(\phi_{\text{h-b}}\) the field in a 3D space, \(A\) the total number of selected atoms, \(\mu_{\text{h-b}} (= 2.5~\text{Å})\) the mean (distance H-bond / receptor), \(d_a\) the distance between the atom position and any point, \(\sigma_{\text{h-b}}^2\) (with \(\sigma_{\text{h-b}} = 0.5~\text{Å}\)) the variance (distance H-bond / receptor).


::: src.smiffer.grid.property_strategy.class_h_bond
