# Theory supplement — draft analytic results (E8, E9, E10)

**Status**: draft for adversarial review. Every claim below is either a *proof* (fully written out,
checkable line by line), a *proposal* (a restatement I recommend but which the authors must
approve), or an *open question* (flagged as such in §5). Nothing here is empirical; no GPU was
used.

**Provenance**: derived by re-reading §4.1, Appendix A (Lemmas 1–8), Appendix C (term-④ algebra)
and Appendix B of the v0.4.17 manuscript, in response to a panel objection (gpt-5.6-sol, item 6)
and to the "not measured" rows of Appendix G.

**Notation.** $R_S,R_T$ are the source/target population risks; $\theta^*_S,\theta^*_T$ their
minimisers; $\Delta:=\theta^*_S-\theta^*_T$; $\widehat\Delta:=\Delta/\|\Delta\|$;
$H_T=\nabla^2R_T$. Constants as printed in Theorem 1: $C_1=2L$, $C_4=2L'\sqrt{L/\mu_T}$,
$C_3=2L/\mu_T$. $\|H\|_2:=\max(\lambda_{\max}(H),-\lambda_{\min}(H))$ is the spectral norm.

---

## 0. Summary

| # | Finding | Kind | Consequence |
|---|---|---|---|
| **A** | Term ④ is *non-negative by optimality* (④ ≥ 0), so Lemma 4 gives $a\ge b$ with $a:=\nabla R_T(\theta^*_S)^\top\Delta$, $b:=\tfrac12\Delta^\top H_T(\xi)\Delta$ | proof | enables the case split below |
| **B** | **Under the paper's own H5, the interaction term $C_3W_1\lambda_{\max}$ is unnecessary**: H5 ⟹ $b>0$ ⟹ $④\le a\le C_4W_1^{3/2}$ | proof | the printed bound is valid but the curvature term is *pure slack* under the paper's assumptions |
| **C** | **When the curvature term *is* needed ($b<0$), $\lambda_{\max}$ may fail to bound it**: $\vert\Delta^\top H\Delta\vert\le\|H\|_2\|\Delta\|^2$, and $\|H\|_2=\lambda_{\max}$ only if $\lambda_{\max}\ge-\lambda_{\min}$; if $H_T$ has a negative eigenvalue of larger magnitude, the printed step-5 chain is **invalid** | proof (counterexample in §1.4) | either substitute $\|H_T\|_2$, or (better) use the directional form |
| **D** | The sharp object is the **negative part of the directional curvature along $\Delta$**: $\kappa^-_\Delta(H):=\max\{0,\,-\widehat\Delta^\top H\widehat\Delta\}$. It is *exactly* necessary (it appears iff needed), *valid* without H5 or PSD-ness, and *measurable by one Hessian-vector product* | proposal | revised Theorem 1′ below; also makes the "geometry" term empirically instantiable |
| **E** | **H5 can be removed altogether**: in the derivation, H5 enters only through $\tfrac12\mu_T\|\Delta\|^2\le④$, so defining $\mu_T^\Delta:=2④/\|\Delta\|^2$ (pair-specific, *measurable*) removes the assumption; Lemma 3 then becomes equivalent to $④\le2LW_1$, which is proved independently | proof + proposal | Appendix G's "μ_T: unknown; not directly measurable" becomes a measured quantity |
| **F** | The $W_1$ ↔ measured-$D$ link is **one-directional**: $D_{\text{meas}}\le C_gW_1+({\rm label\ term})$ is provable in general, the converse needs a bi-Lipschitz encoder | proof | instantiating the bound with the measured $D$ is a *heuristic*, not a certified bound — state this explicitly |
| **G** | $L$ (and $L'$) can be given **explicitly** from H6 + architecture Lipschitz constants, so "bounded log-loss" does not require clipping | proof sketch | answers the reviewer's point 4 by changing the argument, not the protocol |

**The single most important item is C+B.** Taken together they say: *as printed, the interaction
term is either unnecessary (under the stated assumptions) or unbounded-by-the-stated-quantity (when
it is needed).* Both horns are fixable in a few lines, and the fix makes the term **both necessary
and measurable** — which is exactly the "prove that the curvature term is necessary or
informative" that the reviewer demanded.

---

## 1. E9 — Term ④: necessity, a validity gap, and the corrected form

### 1.1 Setup

Lemma 4 of Appendix A is the exact second-order identity (expanding about $\theta^*_S$ and
evaluating at $\theta^*_T=\theta^*_S-\Delta$):

$$④\;:=\;R_T(\theta^*_S)-R_T(\theta^*_T)\;=\;\underbrace{\nabla R_T(\theta^*_S)^\top\Delta}_{=:\,a}\;-\;\underbrace{\tfrac12\Delta^\top H_T(\xi)\Delta}_{=:\,b},\qquad \xi\in[\theta^*_T,\theta^*_S].\tag{L4}$$

*Verification of the sign* (the erratum since v0.4.14): $R_T(\theta^*_T)=R_T(\theta^*_S)+\nabla R_T(\theta^*_S)^\top(-\Delta)+\tfrac12(-\Delta)^\top H_T(\xi)(-\Delta)=R_T(\theta^*_S)-a+b$, hence $R_T(\theta^*_S)-R_T(\theta^*_T)=a-b$. ✔

### 1.2 Result A — ④ ≥ 0, hence $a\ge b$

Because $\theta^*_T$ minimises $R_T$, $④\ge0$. With (L4): **$a\ge b$.** This is used throughout below
and is not exploited anywhere in the submitted manuscript.

### 1.3 Result B — under H5 the curvature term is unnecessary

H5 states $R_T(\theta)-R_T(\theta^*_T)\ge\tfrac12\mu_T\|\theta-\theta^*_T\|^2$ for
$\|\theta-\theta^*_T\|\le r_T$ with $\mu_T>0$; equivalently $H_T(\theta)\succeq\mu_T I$ on that ball,
and **H10 is precisely what places $\xi$ (and $\theta^*_S$) inside it**. Hence
$H_T(\xi)\succeq\mu_T I\succ0$, so $b=\tfrac12\Delta^\top H_T(\xi)\Delta\ge\tfrac12\mu_T\|\Delta\|^2>0$.

Therefore $a\ge b\ge0$, and

$$④=a-b\;\le\;a\;=\;\nabla R_T(\theta^*_S)^\top\Delta\;\le\;\|\nabla R_T(\theta^*_S)\|\,\|\Delta\|\;\le\;L'W_1\cdot\sqrt{4LW_1/\mu_T}\;=\;C_4W_1^{3/2},$$

using Lemma 2 ($\nabla R_S(\theta^*_S)=0$) and Lemma 3. **The bound $④\le C_4W_1^{3/2}$ holds with
no curvature term at all.** ∎

*Slack of the printed form.* The submitted step 5 bounds $|a-b|\le|a|+|b|$. In this regime
$|a|+|b|=a+b=(a-b)+2b$, so the printed bound exceeds $④$ by exactly $2b=\Delta^\top H_T(\xi)\Delta\ge\mu_T\|\Delta\|^2$ — and because $C_3W_1\lambda_{\max}$ is precisely the contribution of that
slack, **the interaction term as printed carries no information about $④$ under the paper's own
assumptions.** (It is not *wrong*; it is *not needed*.)

> Note the logical tension this creates in the present text: Appendix C step 1 motivates the sign
> discussion by saying "the quadratic term is negative", but H5 (assumed throughout) forces
> $b>0$. Both statements cannot describe the same regime.

### 1.4 Result C — a validity gap when the term *is* needed

Suppose instead $b<0$ (negative curvature along the displacement, i.e. a saddle-like crossing).
Then $④=a+|b|$ and a curvature bound is genuinely required. The printed chain uses

$$|b|=\tfrac12|\Delta^\top H_T(\xi)\Delta|\;\le\;\tfrac12\lambda_{\max}(H_T(\xi))\,\|\Delta\|^2,$$

which **holds only if $\lambda_{\max}(H_T(\xi))\ge-\lambda_{\min}(H_T(\xi))$.** For a symmetric
matrix the correct modulus is the spectral norm $\|H\|_2=\max(\lambda_{\max},-\lambda_{\min})$,
since $|x^\top Hx|\le\|H\|_2\|x\|^2$.

**Counterexample (explicit).** $H=\mathrm{diag}(-10,\,1)$, $\Delta\propto e_1$:
$|\Delta^\top H\Delta|=10\|\Delta\|^2$, while $\lambda_{\max}(H)\|\Delta\|^2=1\cdot\|\Delta\|^2$.
The printed bound underestimates the curvature contribution by a factor of 10. Since $b<0$ is
*exactly* the situation in which a large negative eigenvalue is what makes $|b|$ large, the printed
coefficient is unreliable **precisely in the regime where it is doing work**.

**Minimal repair (keeps the printed shape).** Replace $\lambda_{\max}(H_T(\theta))$ by
$\|H_T(\theta)\|_2$; Lemma 7 transfers verbatim because Weyl's inequality bounds the spectral norm
too, so only the symbol changes. $C_3$ is unchanged.

### 1.5 Result D — the sharp object, and the matching example

Define the **negative part of the directional curvature along the displacement**

$$\kappa^-_\Delta(H)\;:=\;\max\bigl\{0,\;-\widehat\Delta^\top H\,\widehat\Delta\bigr\}.$$

Then $b<0\iff\widehat\Delta^\top H_T(\xi)\widehat\Delta<0$, and in that case
$|b|\le\tfrac12\kappa^-_\Delta(H_T(\xi))\|\Delta\|^2$, with equality when $\xi$'s curvature along
$\widehat\Delta$ is the relevant one. Combining with Lemma 3 and Lemma 7:

$$④\;\le\;C_4W_1^{3/2}\;+\;C_3\,\kappa^-_\Delta\!\bigl(H_T(\theta)\bigr)\,W_1\;+\;\mathcal{O}\Bigl(\beta_H(\tfrac{L}{\mu_T})^{3/2}W_1^{3/2}+\beta_H\tfrac{L}{\mu_T}\|\theta-\theta^*_S\|W_1\Bigr).$$

$\kappa^-_\Delta$ is **exactly necessary**: it is $0$ precisely when no curvature term is needed
(Result B's regime), and it is the correct modulus when one is (Result C's regime). It is also
**measurable by a single Hessian-vector product**, since $\Delta$ is the displacement between two
computed endpoints: $\kappa^-_\Delta(H_T)=\max\{0,-\Delta^\top H_T\Delta/\|\Delta\|^2\}$.

**Matching example (quadratic model, both directions).** Let
$R_T(\theta)=\tfrac12(\theta-\theta_T)^\top B(\theta-\theta_T)$, $R_S(\theta)=\tfrac12(\theta-\theta_S)^\top A(\theta-\theta_S)$ with $A,B\succ0$; then (L4) is *exact* with $H_T\equiv B$:
$④=\Delta^\top B\Delta-\tfrac12\Delta^\top B\Delta=\tfrac12\Delta^\top B\Delta$.

- *Aligned case:* $B=\lambda uu^\top+\epsilon(I-uu^\top)$, $\Delta=tu$. Then $④=\tfrac12\lambda t^2$ and
  $\kappa^-_\Delta=0$, while $a=\lambda t^2$, so $④\le a$ — the displacement cost is bounded by the
  first-order term, and the curvature term contributes nothing.
- *Misaligned case:* $\Delta=tv$ with $v\perp u$. Then $④=\tfrac12\epsilon t^2$ (small), while
  $\lambda_{\max}(B)=\lambda$ (large). Substituting $\lambda_{\max}$ into the printed coefficient
  gives a contribution $\tfrac12\lambda t^2$, i.e. the printed bound overestimates $④$ by the ratio
  $\lambda/\epsilon$, **which diverges** as $\epsilon\to0$ at fixed $④$. The directional form gives
  $\kappa^-_\Delta=0$ and no overestimate.

So: **with $\lambda_{\max}$ the term is direction-blind and can be arbitrarily loose; with
$\kappa^-_\Delta$ it is tight up to the transfer constant.** That is the sense in which the
interaction is "necessary or informative" — and the sense in which the printed version is not.

**One nuance that must be stated, to avoid an easy rebuttal.** In the *aligned* case the printed
curvature contribution $C_3W_1\lambda_{\max}$ is numerically **equal** to $④$ (the ratio is 1 in
$\S$V5), so a reader may object that the term *is* informative there. The correct reply is: it is
informative **only in the regime where it is also redundant**. Because $b\ge0$ there, the chain
$④\le a\le\|\nabla R_T(\theta^*_S)\|\|\Delta\|\le C_4W_1^{3/2}$ already bounds $④$ without any
curvature term; the coincidence in magnitude does not make the term carry information the bound did
not already have. In the misaligned case the same term is loose by an unbounded factor. So the term
is (i) redundant when it is accurate and (ii) inaccurate when it is needed — which is exactly why the
directional form is the right restatement.

### 1.6 Proposed revised statement (Theorem 1′) — for author approval

> **Theorem 1′.** Under H1–H4, H6, H8 (H5 not required; see §2), for any $\theta\in\Theta$:
> $$\mathrm{Gap}_T(\theta)\;\le\;R_S(\theta)+C_1W_1+C_4W_1^{3/2}+C_3\,\kappa^-_\Delta\!\bigl(H_T(\theta)\bigr)W_1+\mathcal{O}(\cdot),$$
> with $\kappa^-_\Delta(H)=\max\{0,-\widehat\Delta^\top H\widehat\Delta\}$, and where the term
> $C_3W_1\lambda_{\max}(H_T(\theta))$ is recovered as a (looser, direction-blind) upper bound valid
> when $H_T(\theta)\succeq0$ or $\lambda_{\max}\ge-\lambda_{\min}$.
>
> Interpretation, to be stated at the claim: **target geometry enters the gap only through a
> *negative* curvature along the source→target displacement.** A displacement through
> non-negatively-curved territory costs $C_4W_1^{3/2}$ and nothing more.

---

## 2. E10 — Removing H5, and making the constants measurable

### 2.1 Lemma 3 is an identity in disguise

Lemma 3 ($\|\Delta\|\le\sqrt{4LW_1/\mu_T}$) is proved from H5's quadratic growth at $\theta^*_S$
relative to $\theta^*_T$, i.e. from $\tfrac12\mu_T\|\Delta\|^2\le④$, together with

$$④=R_T(\theta^*_S)-R_T(\theta^*_T)\;\le\;\underbrace{\bigl[R_T(\theta^*_S)-R_S(\theta^*_S)\bigr]}_{\le LW_1\ \text{(Lemma 1)}}+\underbrace{\bigl[R_S(\theta^*_T)-R_T(\theta^*_T)\bigr]}_{\le LW_1\ \text{(Lemma 1)}}\;\le\;2LW_1,$$

where the first inequality uses $R_S(\theta^*_S)\le R_S(\theta^*_T)$ (source optimality). Hence

$$\boxed{\;④\;\le\;2LW_1\;}\tag{★}$$

with **no strong-convexity assumption** — only Lemma 1 twice and the two optimalities. Note also
that $(★)$ and H5's growth inequality together give Lemma 3, so **Lemma 3 adds no assumption
beyond $(★)$.**

### 2.2 Proposal: replace $\mu_T$ by the pair-specific, measured $\mu_T^\Delta$

Define $\mu_T^\Delta:=2\,④/\|\Delta\|^2$ (when $\Delta\ne0$). Then:

- H5's growth inequality holds *by definition*, with equality;
- Lemma 3 holds, since it is equivalent to $(★)$;
- Theorem 1 holds with $\mu_T\to\mu_T^\Delta$, i.e.
  $C_3=\dfrac{L\|\Delta\|^2}{④}$ and $C_4=L'\|\Delta\|\sqrt{2L/④}$;
- **$④$, $\Delta$ are both measurable at endpoints** ($④$ is the target gap at the source endpoint;
  $\Delta$ the parameter distance between the two endpoints), and $L$ has the explicit form of §2.4.

**Consistency check (quadratic model).** With $④=\tfrac12\Delta^\top B\Delta$, the interaction
coefficient reads $C_3\kappa^-_\Delta W_1=\bigl(L\|\Delta\|^2/④\bigr)\kappa^-_\Delta W_1$. For the
bound to dominate the true $|b|=\tfrac12\kappa^-_\Delta\|\Delta\|^2$ we need $LW_1/④\ge\tfrac12$, i.e.
$④\le2LW_1$ — which is exactly $(★)$. ✔ The pair-specific formulation is therefore self-consistent,
and *strictly weaker in assumptions* than the printed one.

**Caveat to state in the paper.** $\mu_T^\Delta$ is a *pair-specific* quantity, not a property of the
target domain: it must not be transported to other $\theta$, and $C_3,C_4$ must be recomputed per
cell. This is a feature for this paper (its constants were never calibrated anyway) but it changes
the theorem's epistemic status from "bound under assumptions" to "identity-based decomposition with
measured coefficients".

### 2.3 What to assume instead of H5

If the authors prefer to keep a named assumption, the weakest one that the derivation actually uses
is the **pair-specific one-sided growth condition**

> **H5′.** $R_T(\theta^*_S)-R_T(\theta^*_T)\;\ge\;\tfrac12\mu_T\|\theta^*_S-\theta^*_T\|^2$ for the
> specific pair $(\theta^*_S,\theta^*_T)$,

which is implied by H5 but requires no eigenvalue lower bound anywhere, and is **directly checkable**
at any cell (both sides are computable). Recommend H5′ + $(★)$ and deleting the ball/radius
machinery of H5 and H10 from the critical path (H10 can stay as a remark on when the displacement
bound linearises).

### 2.4 Result G — an explicit $L$ (the "bounded log-loss" point)

The reviewer is right that BCE-with-logits is unbounded in the logits. Two repairs, neither of which
touches the protocol:

1. *Bounded logits from H6.* Under H6 ($\|\theta\|\le B_\Theta$) and standard architecture
   Lipschitz bounds, the logits satisfy $\|z\|\le\|W_{\text{head}}\|_2\,\|f(\theta;x)\|+\|b\|\le \bar z$,
   with $\bar z$ an explicit product of layer spectral norms; BCE then has $L\le \bar z$ on that
   domain. The spectral norms are measurable by power iteration (same routine as E3).
2. *Box terms.* IoU/Shape-IoU are $[0,1]$-valued by construction, so their data-Lipschitz constants
   are bounded and explicit; only the assignment step is non-smooth, which §2.5 handles.

State $L=\max(L_{\rm cls},L_{\rm box})$ explicitly and mark it as *bounded on the H6 domain*, not
globally. That replaces a false global claim with a true restricted one.

### 2.5 Result H (cross-reference to G2) — where H3/H4 can come from

Not proved here, but the structure is favourable and worth stating: the detector's assignment
(matcher/TAL) is **locally constant**, so on an open region where the assignment does not change, the
loss is a fixed smooth composition of IoU- and BCE-type terms and H3/H4 hold there. The empirical
question is only whether the perturbation radii actually used
($\rho\in\{0.001,0.003,0.01\}$) stay inside such a region — a measurable flip-rate (experiment E2).
This converts "away from non-differentiable points" from an assertion into a *checked* statement.

---

## 3. E8 — Proxy transfer: the measured $D$ versus the theorem's $W_1$

The reviewer's point 5 is correct and the honest answer has two halves.

**What is provable (one direction).** Let $g$ be the frozen encoder used for the shift measurement
and $f(z):=(g(x),y)$ the corresponding data map, with $\mathrm{Lip}(g)=C_g$ on the support. Then
pushforward is Lipschitz in $W_1$, and the label term is separately controlled, so

$$D_{\text{meas}}\;\le\;C_g\,W_1(\mu_S,\mu_T)\;+\;\text{(label term)}.$$

**What is *not* provable.** The converse, $W_1\le\widetilde C_g D_{\text{meas}}$, needs $g$ to be
bi-Lipschitz on the support (an inverse-Lipschitz constant); feature maps collapse directions in
general, and no such bound can hold without an assumption. Consequently:

> Instantiating Theorem 1 with $W_1\leftarrow D_{\text{meas}}$ is justified only up to the constant
> $C_g$ **and only as a lower estimate of the true shift**; the resulting number is a heuristic
> magnitude, not a certified bound. This should be stated where the proxy is introduced (§3.2),
> alongside the existing "constants not calibrated" remark.

**Two things this gives us.**
1. The form of the bound is unchanged — only constants acquire a $C_g$ factor (and $C_g$ per cell).
2. Both $C_g$ and the *failure* of the converse are measurable: $C_g$ by power iteration on the
   encoder Jacobian, and the one-sidedness by comparing the feature-space $W_1$ against a
   data-space (pixel-level) sliced $W_1$ on the same pairs. If those two differ by a large factor,
   the paper can *quantify* the proxy gap instead of only disclosing it — a much stronger position.

---

## 4. What each result needs measured (feeds the A-machine read suite)

| Result | Needs | How | Cost |
|---|---|---|---|
| B | sign of $b$ at endpoints, i.e. $\widehat\Delta^\top H_T\Delta$ | one HVP per endpoint (Δ known) | minutes |
| C, D | $\kappa^-_\Delta(H_T)$ and $\|H_T\|_2$ (for the comparison) | HVP for $\kappa^-$; Lanczos for the spectral norm | 20–50 HVP/endpoint |
| E | $④$ and $\|\Delta\|$ per cell | gap from the run tables; $\|\Delta\|$ between released endpoints | free (existing artefacts) |
| G | $\bar z$, layer spectral norms | power iteration | minutes |
| H (G2) | assignment flip-rate at $\rho\in\{0.001,0.003,0.01\}$ | forward passes | ≈1 h |
| F | $C_g$; feature-space vs pixel-space $W_1$ | power iteration; one extra shift run | minutes + 1 short job |

Together: **all of it fits in the ≈3–6 GPU·h read suite already scoped**, and none of it needs new
training.

---

## 5. Where I could be wrong (please attack these first)

1. **The claim that H5 forces $b>0$.** This rests on reading H5 as $H_T\succeq\mu_TI$ on the ball and
   H10 as placing $\xi$ inside it. If the intended reading of H5 is weaker (e.g. growth only along
   specific directions, or only at $\theta^*_T$ rather than on the segment), Result B needs
   restating. **This is the single claim most worth checking.**
2. **Whether bounding $④$ (rather than $|④|$) is admissible.** I use $④\ge0$; if the authors need
   $|R_T(\theta^*_S)-R_T(\theta^*_T)|$ for a *different* telescoping arrangement, the case split
   changes. In Eq. (3) as printed, ④ enters with a plus sign and is non-negative, so bounding ④
   suffices.
3. **Whether $\mu_T^\Delta$ is acceptable as a replacement for an assumed constant.** It removes an
   assumption but weakens the statement's universality (the constant becomes data-dependent). Some
   referees will prefer the assumption; that is a presentation choice, not a mathematical one.
4. **Whether $\kappa^-_\Delta$ is the tightest available modulus.** It is tight *along $\Delta$*;
   a version depending on the whole segment (e.g. $\min_{\xi}$ along it) would be tighter still and
   is probably not worth the complexity.
5. **The misaligned-case divergence argument** assumes $\epsilon$ can be taken to $0$ while keeping
   the other hypotheses (in particular Lemma 3's link between $\|\Delta\|$ and $W_1$) satisfiable.
   In the bare quadratic model that is free; inside the full theorem's dependency structure it should
   be re-checked.
