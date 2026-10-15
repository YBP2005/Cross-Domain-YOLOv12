# Theory supplement — v2 (post-referee revision)

**What this is.** v1 of this note proposed changing the interaction term of the paper's Theorem 1.
It was sent to two external referees for adversarial checking (grok-4.6 and gpt-5.6-sol). Both
accepted the *central* finding; they disagreed sharply on the *proposed replacement*, and gpt-5.6-sol
identified **five statements in v1 that are mathematically wrong rather than incomplete**. Three of
those are accepted here and corrected. This v2 supersedes v1; v1 is retained unedited as the artefact
that was reviewed (`theory_supplement_draft_E8_E9_E10.md`).

**Referee verdicts at a glance**

| Result | grok-4.6 | gpt-5.6-sol | v2 status |
|---|---|---|---|
| A (④ ≥ 0 ⇒ a ≥ b) | accept | accept | **stands** |
| B (curvature term redundant) | accept | accept **only** under genuine (two-point) strong convexity | **conditional — restated in §2** |
| C (λ_max can fail to bound \|ΔᵀHΔ\|) | accept | accept the counterexample and the spectral-norm repair | **stands — the headline, reading-independent** |
| D (κ⁻_Δ replacement) | accept | accept the one-sided inequality; reject "uniformly tighter"/"absolutely necessary" | **restated in §3** |
| E (delete H5 via μ_T^Δ) | accept with a comparability caveat | **reject** as a deletion of an assumption | **recast as a diagnostic, not a deletion (§4)** |
| F (proxy is one-directional) | accept | accept, but v1 *understated* it and got the direction wrong | **corrected in §5** |
| G (explicit L) | accept as a sketch | **reject as stated** | **corrected in §6** |

**The one thing that survives every objection:** as printed, the curvature magnitude is bounded by
$\lambda_{\max}$, and $\lambda_{\max}$ is **not a valid modulus for $\vert\Delta^\top H\Delta\vert$**
when the Hessian has a negative eigenvalue of larger magnitude — which is precisely the regime in
which a curvature term is needed. That is a *validity* issue, and it is independent of how H5 is read.

---

## 1. Result C — the reading-independent finding (unchanged, accepted)

Appendix C step 5 bounds the curvature magnitude by
$\tfrac12\lambda_{\max}(H_T(\xi))\|\Delta\|^2$. For a symmetric matrix the correct uniform modulus is
the spectral norm $\|H\|_2=\max(\lambda_{\max},-\lambda_{\min})$, because
$\vert x^\top Hx\vert\le\|H\|_2\|x\|^2$. The printed form is valid only if
$\lambda_{\max}\ge-\lambda_{\min}$.

**Counterexample.** $H=\mathrm{diag}(-10,1)$, $\Delta\propto e_1$:
$\vert\Delta^\top H\Delta\vert=10\|\Delta\|^2$ but $\lambda_{\max}\|\Delta\|^2=1\cdot\|\Delta\|^2$.
Numerically verified (`verify_referee_objections.py`, checks O2).

*Referee qualification accepted* (gpt-5.6-sol): the condition $\lambda_{\max}\ge-\lambda_{\min}$ is
what makes the bound valid **uniformly over directions**; for a *particular* $\Delta$ it can hold even
when the condition fails. So the correct phrasing is "valid uniformly only if …", not "valid only if".
The one-sided point nevertheless survives: when $b<0$, a large negative eigenvalue is exactly what
makes $\vert b\vert$ large, and $\lambda_{\max}$ does not control it.

**Minimal repair (keeps the printed shape).** Replace $\lambda_{\max}(H_T(\theta))$ by
$\|H_T(\theta)\|_2$. Lemma 7 transfers verbatim (Weyl bounds the spectral norm too); $C_3$ unchanged.

---

## 2. Result B — restated as conditional (v1 was too strong)

v1 asserted that H5 "$\iff H_T(\theta)\succeq\mu_T I$ on the ball". **That equivalence is false and
gpt-5.6-sol's counterexample is verified here.** For
$f(x)=x^2+\epsilon(1-\cos kx)$: $f(x)\ge x^2$ everywhere (growth holds with $\mu=2$), $f'(0)=0$, yet
$f''(x)=2+\epsilon k^2\cos(kx)$ satisfies $f''<0$ on a set of positive measure — numerically
$\min f''=-15.82$ on $(-0.5,0.5)$ at $\epsilon k^2=18$. **One-point quadratic growth does not imply
pointwise Hessian positivity.**

Corrected statement:

> **Result B′.** If H5 is **genuine local strong convexity** — the two-point inequality
> $R_T(y)\ge R_T(x)+\nabla R_T(x)^\top(y-x)+\tfrac12\mu_T\|y-x\|^2$ for all $x,y$ in the radius-$r_T$
> ball — then for $C^2$ risks $H_T\succeq\mu_T I$ there, and provided the segment
> $[\theta^*_T,\theta^*_S]$ lies in the ball, $b\ge\tfrac12\mu_T\|\Delta\|^2\ge0$; hence
> $④\le a\le C_4W_1^{3/2}$ and **the curvature term is redundant**. Under only the weaker
> one-point growth condition, this does **not** follow.

The manuscript names H5 "target-side local **strong convexity** (μ_T, radius r_T)" — which supports the
strong reading — while Appendix C step 3 *uses* it as "H5's quadratic growth". **The paper should say
explicitly which reading is intended**, because Result B′ turns on it. (Edge case noted by
gpt-5.6-sol: if $\Delta=0$ then $b=0$, not $>0$; harmless.)

---

## 3. Result D — restated without the overclaims

Define $q_\Delta(H):=\widehat\Delta^\top H\widehat\Delta$ and
$\kappa^-_\Delta(H):=\max\{0,-q_\Delta(H)\}$. The identity $④=a-\tfrac12\|\Delta\|^2q_\Delta(H_T(\xi))$
gives $④\le\vert a\vert+\tfrac12\|\Delta\|^2\kappa^-_\Delta(H_T(\xi))$ — a valid one-sided bound
**with no PSD assumption**, retaining only the adverse directional curvature. Transferring from $\xi$ to
$\theta$ requires $\kappa^-_\Delta(H_T(\xi))\le\kappa^-_\Delta(H_T(\theta))+\|H_T(\xi)-H_T(\theta)\|_2$
(Lemma 7's remainder).

**Three claims from v1 are withdrawn or weakened** (all three flagged by gpt-5.6-sol and accepted):

1. ~~"uniformly tighter than $\lambda_{\max}$"~~ → **no uniform ordering exists.** The verified
   ordering facts are: $H\succeq0\Rightarrow\kappa^-_\Delta=0$; if $\lambda_{\max}\ge-\lambda_{\min}$
   then $\kappa^-_\Delta\le\lambda_{\max}$; otherwise there is no ordering (on the indefinite example
   $\kappa^-_\Delta=10>\lambda_{\max}=1$, where $\lambda_{\max}$ is *invalid*). The right claim is
   that $\kappa^-_\Delta$ is **valid** where $\lambda_{\max}$ is not, and is zero exactly when the
   Taylor quadratic term is non-negative.
2. ~~"exactly necessary"~~ → it is **the minimal correction for this particular Taylor
   decomposition** (zero iff that quadratic term is non-negative), not necessary in an absolute
   theorem-level sense: another estimate could absorb negative curvature differently.
3. The misaligned example needs three qualifications: (i) $\Delta\perp v_{\max}$ alone does not give
   divergence — a diverging eigenvalue *ratio* is also needed; (ii) the quantity compared is the
   **intermediate quadratic estimate** $\tfrac12\lambda\|\Delta\|^2$, not the final theorem term
   $C_3W_1\lambda$ (equality of the latter would require saturation of the displacement bound);
   (iii) taking $\epsilon\to0$ at fixed $④$ forces $\|\Delta\|\to\infty$, so compatibility with the
   bounded-parameter-domain assumption (H6) is **not** established. The example therefore proves
   *algebraic direction-blindness*, not the existence of an admissible full-theorem family.

*Measurability, corrected.* "One Hessian-vector product" applies to the **empirical** Hessian at the
**computed** endpoints; it does not make the *population* $\Delta$ or $H_T$ measurable. The
empirical→population step is exactly the uniform-convergence surcharge the paper already keeps outside
Theorem 1.

---

## 4. Result E — recast: an a posteriori diagnostic, not a deletion of H5

v1 proposed deleting H5 by defining $\mu_T^\Delta:=2④/\|\Delta\|^2$. grok-4.6 accepted it with a
comparability caveat; **gpt-5.6-sol rejected it outright**, and its reasons are accepted here:

1. **Degenerate case.** If $④=0$ with $\Delta\ne0$ (non-unique/flat minima) then $\mu_T^\Delta=0$ and
   $C_3,C_4$ are undefined or infinite; without growth or uniqueness, $W_1$ need not control the
   distance between arbitrarily chosen minimisers.
2. **Loss of ex-ante uniformity.** A strong-convexity constant is an ex-ante property of a risk on a
   neighbourhood; $2④/\|\Delta\|^2$ is an ex-post ratio for one selected pair, not reusable.
3. **Potential vacuity / circularity.** $④$ is itself a *target population* excess risk; a bound whose
   coefficients require the unknown target optimum is not operational.
4. **Not directly measurable.** Empirical endpoints and empirical risks do not reveal population
   minimisers or population $④$.
5. **Internal tension** (also spotted independently): §2's Result B *uses* H5 to get Hessian
   positivity along the segment, while §4's proposal says H5 enters "only" through the displacement
   inequality. **Both readings cannot be assumed at once**; v1 did not notice this.

Verified (`verify_referee_objections.py`, check O3). **Consequence for the recommendation:** the
displacement inequality $\|\Delta\|\le\sqrt{4LW_1/\mu_T}$ can indeed be replaced by the
assumption-free $(★)\;④\le2LW_1$, but *that is not the same as removing H5 from the theorem*, because
$b\ge0$ (Result B′) also comes from H5. Removing H5 therefore **adds** the negative-curvature case
rather than simplifying it.

*Retained middle road* (proposed by grok-4.6, and it is what v1's own §2.3 said): keep a **named,
minimal, pair-specific** assumption

> **H5′.** $R_T(\theta^*_S)-R_T(\theta^*_T)\ge\tfrac12\mu_T\|\theta^*_S-\theta^*_T\|^2$ for the
> specific pair $(\theta^*_S,\theta^*_T)$,

which is implied by H5, needs no eigenvalue lower bound, and is checkable at any cell. And treat
$\mu_T^\Delta$ only as a **diagnostic** reported alongside, never as a theorem coefficient.

---

## 5. Result F — corrected, and the obstruction v1 missed

**v1 got the direction wrong.** From $D_{\text{meas}}\le C_gW_1$ one gets only
$W_1\ge D_{\text{meas}}/C_g$. Since Theorem 1 is **increasing in $W_1$**, substituting $D$ for $W_1$
makes the bound *smaller* — so the substitution is **not** a valid instantiation, and the sentence in
v1 that "the form is unchanged, only constants acquire a $C_g$ factor" is **withdrawn**. The correct
statement is the one v1 also carried: the available direction gives a *lower* proxy for the shift, so
instantiating the theorem with $D$ yields a heuristic magnitude, not a certified bound.

**A second, independent obstruction** (raised by gpt-5.6-sol, missed in v1): $D$ is a **sliced**
Wasserstein distance. Even with a bi-Lipschitz encoder, a finite-projection sliced distance need not
control the full feature-space transport metric in the same linear form. So a converse would require
assumptions on **both** (i) the encoder (invertibility/inverse-Lipschitzness on the supports, or a
decoder with controlled reconstruction error) **and** (ii) the relation between the sliced proxy and
the full metric. v1's F2 therefore understated the requirement.

**What survives and is still useful:** the one-sidedness, now with an explicit form —
$D_{\text{meas}}\le\sqrt{R_gC_FW_1}+\sqrt{\text{label term}}$ (see the addendum file for the proof,
including the correct $W_2^2\le R_gW_1$ comparison, which v1 also stated wrongly) — and the fact that
$C_F$ and the size of the one-sidedness are **measurable**, so the paper can *quantify* the proxy gap
rather than merely disclose it.

---

## 6. Result G — corrected

v1's §2.4 wrote "$L\le\bar z$ for BCE", which gpt-5.6-sol correctly rejects: **boundedness of a value
is not a Lipschitz constant**, and a bounded function can be discontinuous. The repair (already in the
addendum, written after v1 was sent) does not use boundedness at all:

> $L_{\rm cls}\le\mathrm{Lip}\bigl(u(\theta;\cdot)\bigr)\le\prod_\ell\|W_\ell\|_2\cdot\prod_\ell\mathrm{Lip}(\phi_\ell)$,
> because $\bigl\vert\partial\,\mathrm{BCE}(\sigma(u))/\partial u\bigr\vert=\vert\sigma(u)-y\vert\le1$
> (BCE-as-a-function-of-the-logit is $1$-Lipschitz), and composition multiplies Lipschitz constants.

Also accepted: "IoU is bounded" does **not** imply it is Lipschitz — IoU-type terms need
non-degeneracy assumptions on the box denominators; v1's Prop. G2 must state them.

**Net position on the reviewer's original point:** the reviewer is right that the loss *value* is
unbounded without clipping, and wrong that this matters for H1, which needs a **data-Lipschitz**
constant — finite and explicit here by the composition argument. That is a better answer than
conceding, but it must be made with the composition argument, not with boundedness.

---

## 7. Revised recommendation: two branches (this replaces v1's Theorem 1′)

gpt-5.6-sol's structural point is accepted: v1's Theorem 1′ was **a regression** because it removed H5
while keeping constants that depend on an inadequately defined, pair-specific $\mu_T$, and because it
used population quantities that are not operationally measurable. The cleaner recommendation is a
**case split**, and the authors should pick one:

**Branch 1 — keep H5 as named (genuine local strong convexity) and DELETE the interaction term.**
By Result B′, $④\le C_4W_1^{3/2}$ already, so the curvature term is provably redundant and the theorem
becomes
$$\mathrm{Gap}_T(\theta)\;\le\;R_S(\theta)+C_1W_1+C_4W_1^{3/2}+\mathcal O(\cdot).$$
Minimal edit, strictly valid under the paper's own assumptions, and it removes a term whose constant
was never calibrated. **Cost:** the theory loses its "geometry interacts with shift" flavour — but
that flavour was already declared non-predictive in Appendix J.2, so little is actually lost.

**Branch 2 — keep a geometry term, but fix it.**
(i) Replace $\lambda_{\max}$ by $\kappa^-_\Delta$ (or, minimally, by $\|H_T\|_2$) — this is required in
either branch if the term is retained. (ii) Do **not** lean on H5 for it; state the extra assumption
explicitly (a displacement/stability condition, or H5′). (iii) Report $\kappa^-_\Delta$ and the sign of
$\widehat\Delta^\top H_T\Delta$ at the endpoints as measurements, with the empirical→population
caveat.

**Recommendation: Branch 1**, with $\kappa^-_\Delta$ reported as a *diagnostic* in Appendix J.2. It is
the version both referees would pass, it deletes an uncalibrated constant rather than defending it, and
it keeps the paper's existing "the interaction term is a risk channel, not a validated predictor"
position intact.

---

## 8. Manuscript changes implied (revised)

| # | Location | Change | Kind |
|---|---|---|---|
| 1 | §4.1 box, Appendix A Lemma 3, Appendix C step 3 | State **which reading of H5** is intended; if growth-only, add H5′; record $(★)\;④\le2LW_1$ as assumption-free | correction |
| 2 | Theorem 1 / Eq. (4), Appendix C step 5, Appendix J.1 | Branch 1: **delete** $C_3W_1\lambda_{\max}$ and $C_3$. Branch 2: replace $\lambda_{\max}$ by $\kappa^-_\Delta$ (or $\|H_T\|_2$) and state the added assumption | correction (validity) |
| 3 | §9.1 | Replace "bounded log-loss" with the Lipschitz-in-data statement (composition argument) | correction |
| 4 | §3.2 | Add the one-sided proxy lemma and the **sliced-distance** obstruction; remove any suggestion that the substitution is constant-only | correction |
| 5 | §9.1 / Result H | Replace "away from non-differentiable points" with the local-constancy-of-assignment argument + measured flip rate | correction + measurement |
| 6 | Appendix G | $L$, $L'$: explicit product form; $\mu_T$ row: state the reading and mark H5′ if adopted | strengthening |
| 7 | Appendix J.2 | Report $\kappa^-_\Delta$, sign of $\widehat\Delta^\top H_T\Delta$, and $\|H_T\|_2$ as diagnostics | new content (E1) |

**No empirical claim, no number in §5–§8, and no abstract statement is affected** — the interaction
term is already declared non-predictive, so all of the above is confined to the theory's own status.

---

## 9. What still needs the GPU reads (unchanged scope)

The zero-GPU work is now done: the algebra is settled, the invalidity is established, and the repair is
chosen. What remains is *measurement*, and it is small: the sign and size of
$\widehat\Delta^\top H_T\Delta$ / $\kappa^-_\Delta$ at endpoints, $\|H_T\|_2$ for the comparison,
assignment flip-rates, and the constants $C_F$, $L$. Estimated **≈3–6 GPU·h**, deferred to machine A as
agreed.

## 10. Provenance

- v1 note: `theory_supplement_draft_E8_E9_E10.md` (the artefact reviewed)
- Referee reports: `model_review/ask_theory_x-ai-grok-4.6_20260913_152639.md`,
  `model_review/ask_theory_openai-gpt-5.6-sol_20260913_152644.md`
- Numerical checks of v1's algebra: `work/verify_theory_claims.py` (7 groups, 0 failures)
- Numerical checks of the referees' objections: `work/verify_referee_objections.py` (0 failures)
- Additional proofs (F1/F2, G1/G2): `theory_supplement_addendum_proofs.md`
