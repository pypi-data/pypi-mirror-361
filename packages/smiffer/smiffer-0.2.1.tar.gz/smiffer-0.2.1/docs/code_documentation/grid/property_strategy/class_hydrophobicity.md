# class_hydrophobicity.py

Computation is based on next formula:

$$
\phi_{\text{hydr}} = - \displaystyle\sum_{s=1}^S K_s \displaystyle\sum_{a=1}^{A_s} \exp \left[ - \dfrac{\left( \mu_{\text{hydr}} - d_a \right)^2}{2 \sigma_{\text{hydr}}^2} \right]
$$

With \(\phi*{\text{hydr}}\) the field in a 3D space, \(S\) the total number of selected “chemical specie” (residues, RNA base, sugar or phosphate), \(K_s\) the chemical specie hydrophobicity score (from Kyte Doolittle Scale), \(A_r\) the selected atoms from the residue \(r\), \(\mu*{\text{hydr}} (= 4.0~\text{Å})\) the mean (distance residue / receptor), \(d*a\) the distance, \(\sigma*{\text{hydr}}^2\) (with \(\sigma*\text{hydr}= 1.5~\text{Å})\) the variance (distance residue / receptor).

::: src.smiffer.grid.property_strategy.class_hydrophobicity
