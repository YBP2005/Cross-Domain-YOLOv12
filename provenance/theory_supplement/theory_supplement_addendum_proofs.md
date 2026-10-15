# Theory supplement — addendum: complete proofs for Results F (E8) and G (E10b)

*Addendum to `theory_supplement_draft_E8_E9_E10.md`. The note that was sent out for adversarial
checking did **not** include these proofs; they are written separately so that the provenance of what
was reviewed stays clean. Same notation.*

---

## 6. Result F in full (E8) — the proxy transfer lemma

**Setting.** Let $\mathcal Z$ be the data space (image + annotation) with metric $d$; $\mu_S,\mu_T$
probabilities on $\mathcal Z$. The theorem's $W_1$ is w.r.t. $d$ on $\mathcal Z$. The measured shift
is computed on *frozen backbone features*: let $g:\mathcal X\to\mathbb R^{p}$ be the frozen encoder and
$F(z) := (g(x), y)$ the induced map into feature-plus-label space, with

$$D_{\text{meas}}\;=\;\Bigl(W_2^{\text{feat}}\bigl(g_\#\mu_S,\;g_\#\mu_T\bigr)^2+\text{(label term)}\Bigr)^{1/2}$$

(the released s-OTDD definition: squared feature $W_2$ plus a label term, square-rooted).

**Lemma F1 (forward direction — provable).** Let $R_g:=\mathrm{diam}\bigl(\operatorname{supp}(g_\#\mu)\bigr)<\infty$
be the diameter of the feature support. Suppose the induced map $F(z)=(g(x),y)$ is $C_F$-Lipschitz in
the data metric, $d_{\mathcal Z'}(F(z),F(z'))\le C_F\,d(z,z')$. Then

$$D_{\text{meas}}\;\le\;\sqrt{R_g\,C_F\,W_1(\mu_S,\mu_T)}\;+\;\sqrt{\text{(label term)}}.$$

*Proof.* (i) *Pushforward.* For any coupling $\pi$ of $(\mu_S,\mu_T)$, $(F\times F)_\#\pi$ couples
$F_\#\mu_S$ with $F_\#\mu_T$ at cost $\mathbb E_\pi d_{\mathcal Z'}(F(z),F(z'))\le C_F\,\mathbb E_\pi d(z,z')$;
taking the infimum gives $W_1^{\mathcal Z'}(F_\#\mu_S,F_\#\mu_T)\le C_F\,W_1(\mu_S,\mu_T)$. (ii) *$W_2$ vs
$W_1$ on a bounded support.* Since $d\le R_g$ almost surely for the optimal coupling,
$W_2^2=\inf_\pi\mathbb E_\pi d^2\le R_g\inf_\pi\mathbb E_\pi d=R_g\,W_1$ — note this is a
**square-root, not linear, comparison**, and the same holds after restricting to the feature
coordinates. (iii) Combine with $\sqrt{a+b}\le\sqrt a+\sqrt b$. $\blacksquare$

**Two consequences, both worth stating in the paper.**

1. The measured quantity is a **$W_2$-type object with a label term**, whereas Theorem 1 is stated in
   $W_1$; the two are related only up to the diameter factor $R_g$. So the proxy gap has **two**
   components — feature-space vs data-space (the constant $C_F$) and $W_2$ vs $W_1$ (the factor
   $R_g$) — and both are measurable.
2. Inverting F1: $W_1\;\ge\;\bigl(D_{\text{meas}}-\sqrt{\text{label}}\bigr)^2/(R_gC_F)$. So the true
   shift is bounded below by a quantity **quadratic** in the measured $D$; substituting $D$ for $W_1$
   in Theorem 1 can *understate* the shift substantially, and the statement "the constants are not
   calibrated" should be upgraded to "the substitution is one-sided, with this explicit form".


**Lemma F2 (converse — requires an extra assumption).** If in addition there is a map
$h:\operatorname{supp}(F_\#\mu)\to\mathcal Z$ with $h\circ F=\mathrm{id}$ on the support and
$\mathrm{Lip}(h)=C_h<\infty$ (an *inverse-Lipschitz / bi-Lipschitz* condition), then

$$W_1(\mu_S,\mu_T)\;\le\;C_h\,W_1^{\mathcal Z'}(F_\#\mu_S,F_\#\mu_T).$$

*Proof.* Apply Lemma F1's pushforward argument to $h$. $\blacksquare$

**Why F2 cannot be assumed away.** Feature maps collapse directions: for any target dimension
$p<\dim\mathcal Z$ there exist distributions with $W_1=0$ after $F$ and $W_1>0$ before it (take two
distributions differing only in a direction annihilated by the encoder). Hence **no** bound of the
form $W_1\le\widetilde C D_{\text{meas}}$ holds without an assumption, and a referee is entitled to
demand either F2's bi-Lipschitz condition or the explicit statement that the instantiation is
one-sided. *Recommendation:* state Lemma F1 and the one-sidedness at §3.2, keep the constants
uncalibrated as already declared, and (as a measurement) report the empirical size of the gap in
Result F's second half.

**Remark (what makes this better than a concession).** Both $C_F$ and the size of the one-sidedness
are *measurable*: $C_F$ by power iteration on the encoder Jacobian, and the one-sidedness by comparing
$D$ computed on features against a sliced $W_1$ computed in data space on the same pairs. The paper
therefore has the option to **quantify** the proxy gap rather than merely disclose it.

---

## 7. Result G in full (E10b) — an explicit $L$, and why the reviewer's premise is inverted

**The objection.** "The claim that classification loss is *bounded log-loss* is false unless logits or
probabilities are explicitly clipped."

**Why the objection misidentifies what H1 needs.** H1 requires the loss to be **Lipschitz in the
data**, i.e. $|\ell(\theta;z)-\ell(\theta;z')|\le L\,d(z,z')$ — a bound on a *difference*, not on the
loss *value*. The value of BCE-with-logits is indeed unbounded in the logits, and the objection is
right about that; but that fact is irrelevant to H1, because the *sensitivity to the data* is bounded
by the architecture. The repair is therefore not clipping but an explicit constant, as follows.

**Proposition G1 (explicit $L$ for the classification term).** Let $\sigma$ be the sigmoid and
$\ell_{\rm cls}(\theta;z)=\mathrm{BCE}\bigl(\sigma(u(\theta;x)),\,y\bigr)$ with logit map
$u(\theta;\cdot)$ from images to logits. Then

$$L_{\rm cls}\;\le\;\mathrm{Lip}\bigl(u(\theta;\cdot)\bigr)\;\le\;\prod_{\ell=1}^{D}\|W_\ell\|_2\;\cdot\;\prod_{\ell}\mathrm{Lip}(\phi_\ell),$$

where $W_\ell$ are the weight matrices along the feature path, $\phi_\ell$ the activation functions
(SiLU: $\mathrm{Lip}\le1.1$), and normalization layers contribute their own Lipschitz constants
computed from the frozen running statistics.

*Proof.* For fixed $y$, $\partial\,\mathrm{BCE}(\sigma(u))/\partial u=\sigma(u)-y$, so
$|\sigma(u)-y|\le1$: BCE is $1$-Lipschitz in the logit. Composition multiplies Lipschitz constants,
and the logit map's Lipschitz constant is bounded by the product of layer spectral norms (standard
path-norm bound; the max-plus structure of detection heads only adds a finite constant).
Hence $|\ell_{\rm cls}(\theta;z)-\ell_{\rm cls}(\theta;z')|\le 1\cdot\mathrm{Lip}(u)\cdot d(x,x')$.
$\blacksquare$

**Proposition G2 (box terms).** Shape-IoU and IoU-type terms are $[0,1]$-valued and piecewise smooth
in the box coordinates, whose coordinates are themselves Lipschitz in the image through the regression
head; so $L_{\rm box}$ is finite and bounded by $\mathrm{Lip}(\text{regression head})$ times the
(yields-bounded) derivative of the IoU expression. The assignment step is the only genuinely
non-smooth operation and is handled by Result H (local constancy of the assignment).

**Conclusion.** Set $L=\max(L_{\rm cls},L_{\rm box})$ and state it as *bounded on the H6 parameter
domain*, with the explicit product form. This (i) removes the false global-boundedness claim, (ii)
requires no change to the training protocol, and (iii) makes $L$ **measurable** by the same power
iteration used for $C_F$ — which is what Appendix G currently lists as "not measured".

**Note for the rebuttal.** The honest summary of this exchange is: *the reviewer is right that the
value is unbounded and wrong that this matters for H1; the fix is an explicit constant, not clipping.*
That is a better position than conceding the point.

---

## 8. Consolidated list of manuscript-level changes these results imply

*(presented for author approval; nothing applied yet)*

| # | Location | Change | Kind |
|---|---|---|---|
| 1 | §4.1, Appendix C step 5, Eq. (4), Appendix J.1 | $\lambda_{\max}(H_T(\theta))$ → $\kappa^-_\Delta(H_T(\theta))$ **or** $\|H_T(\theta)\|_2$; recommended: state Theorem 1′ with $\kappa^-_\Delta$ and recover the $\lambda_{\max}$ form as a stated special case | **correction** (Result C is a validity gap) |
| 2 | §4.1 assumptions box; Appendix G row for $\mu_T$; Appendix A Lemma 3 | Replace H5 by H5′ (pair-specific one-sided growth) or delete it via $\mu_T^\Delta:=2④/\|\Delta\|^2$; record $(★)$: $④\le2LW_1$ | **strengthening** (removes an unverified assumption) |
| 3 | Appendix G rows for $L$, $L'$ | Replace "not measured" by the explicit product form (Props. G1–G2) | **strengthening** |
| 4 | §9.1 | Replace "bounded log-loss" with the Lipschitz-in-data statement | **correction** |
| 5 | §3.2 | Add Lemma F1 + the one-sidedness sentence | **correction** (answers a standing objection) |
| 6 | §9.1 / Result H | Replace "away from non-differentiable points" with the local-constancy-of-assignment argument + the measured flip rate (E2) | **correction + measurement** |
| 7 | Appendix J.2 | Report $\kappa^-_\Delta$ and the sign of $\widehat\Delta^\top H_T\Delta$ at endpoints, replacing the "not a predictor" statement with "the term enters only for negative directional curvature, and here is its measured size" | **new content** (E1) |

No empirical claim, no number in §5–§8, and no abstract statement is affected: the interaction term is
already declared non-predictive, so all of this is confined to the theory's own status.
