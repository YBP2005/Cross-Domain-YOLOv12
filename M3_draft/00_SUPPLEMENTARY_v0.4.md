# Supplementary material — A measurement-and-audit protocol for budgeted fine-tuning of lightweight detectors

This file carries the appendices of the manuscript. They are **supplementary material**: not typeset into
the article, published online as supplied, and **not part of the manuscript's page budget**. The letters are
unchanged from the manuscript's cross-references, so "Appendix J.4" in the main text resolves to the section
of that name here. Ordering here is alphabetical (**A–P**, with P added 2026-10-04), and the reference-status ledger follows the
appendices; the manuscript's pointers are unaffected. The internal compression record named in the
reference-status ledger is **not** part of this file and is not supplied.

> ⚠ **On the "(moved from §X)" markers (added 2026-10-02).** Thirty passages below carry a provenance marker of
> the form *"(moved from §8.6)"*. **Those section numbers belong to an earlier version of the manuscript**,
> whose numbering differed from the present article's; they are retained as a record of **where the material
> came from**, and they are **not** live cross-references. In the present article, §5–§9 carry no subsections
> at all, so a pointer such as "§8.6" will not resolve there. The **appendix letters (A–N)** are the live
> pointers: they are what the main text cites.


## Figures carried in this supplement, and how they are cited

These five figures are **carried in this supplementary material** rather than in the article file, so that the article is paginated to the journal's length rule. **As the article stands, none of them is cited from the main text**: the readings they illustrate are reported in the article in tables and in words, and the figures are provided here as the released record of those readings rather than as article figures. Where a figure is referred to below, the pointer is to the section of this supplement that reports the reading. (The protocol schematic, **Fig. 1**, is carried in the article file itself and is the article's only figure.)

**Fig. S1. Budget curve, SHWD→SFCHD** — point estimates +1.00 / +0.65 / +0.51 pp at 30 / 50 / 100 epochs (3 seeds each): the gain decreasing as the budget grows, then plateauing (+0.52 pp at 200 epochs).

**Fig. S2. Shift ordering (heuristic)** — +0.07 (D = 9.44) / +0.51 (D = 12.76) / +1.78 (D = 12.99); a two-segment heuristic (D < 10 vs. D ≈ 13) on three points whose label spaces are not equivalent.

**Fig. S3. Dual-metric separation** — at 100 epochs strategy gains turn negative in mAP50 while staying non-negative in mAP50-95 in **4 of the 15** long-budget cells (the per-cell signs and the marginals are in Table T12).

**Fig. S4. Measurement-hierarchy schematic** — trajectory-evaluated first-order reads (worst-direction increments, gradient norms, alignment cosines) against second-order stationary reads; the proposition bans a *use*, not the quantities.

**Fig. S5. Prediction–evidence–status matrix** — per-prediction status across §6–§7 (four evidence lines; SNR floor 18/18 < 2).

# Appendix A. Lemmas used by the bound, and the linear displacement refinement

**Statements (assumption numbering H1–H10 as in Appendix J.1; proofs are carried in a theory supplement available from the authors; **the proofs are not part of this release**, so the lemmas below are stated without them).**

- **Lemma 1 (Kantorovich–Rubinstein duality; H1).** For any $\theta$, $|R_T(\theta)-R_S(\theta)| \le L\,W_1(\mu_S,\mu_T)$.
- **Lemma 2 (gradient-domain KR; H2).** $\|\nabla R_T(\theta)-\nabla R_S(\theta)\| \le L'\,W_1(\mu_S,\mu_T)$. *(Standard bookkeeping, supplied in that theory supplement: the interchange $\nabla R = \mathbb E[\nabla\ell]$ requires measurability of $\nabla\ell(\theta,\cdot)$, integrability, and the usual dominated-convergence conditions along the differentiating directions; H2 is a statement about $\nabla\ell$ and presupposes its differentiability in $\theta$, rather than implying it.)*
- **Lemma 3 (optimal-displacement bound; H1 and H5 in its ball form, together with the localization of $\theta^*_S$ — H8 does not belong to this footprint).** $\|\theta^*_S-\theta^*_T\| \le \sqrt{4LW_1/\mu_T}$. *(Two corrections of record. First the constant: $\sqrt{4LW_1/\mu_T}$ follows from the **linear** branch, $\text{④}\le2LW_1$, combined with the two-point strong-convexity inequality, $\tfrac{\mu_T}{2}\|\Delta\|^2\le\text{④}\le2LW_1$. Routing the same inequality through the single-KR bound $\text{④}\le LW_1$ gives the sharper $\sqrt{2LW_1/\mu_T}$; we print the looser form because it matches H10's normalisation $W_1\le\mu_T r_T^2/4L$, so that H10 and this lemma use one and the same radius scale rather than two. Second the hypothesis list: the derivation applies the two-point inequality to the pair $(\theta^*_S,\theta^*_T)$, so it **presupposes** the localization stated in Appendix J and Appendix C step 1 and cannot be used to establish it — no circularity is available. It uses no Taylor identity and no $C^2$ regularity, so H8 is not in the footprint.)*
- **Lemma 4 (second-order expansion; H8, not H3 — label corrected).** $R_T(\theta^*_S)-R_T(\theta^*_T) = \nabla R_T(\theta^*_S)^\top\Delta - \tfrac12 \Delta^\top H_T(\xi)\Delta$ with $\Delta := \theta^*_S-\theta^*_T$ and $\xi$ on the segment between $\theta^*_S$ and $\theta^*_T$. Expand about $\theta^*_S$ and evaluate at $\theta^*_T = \theta^*_S - \Delta$: the second-order term carries a minus sign. An earlier version printed $+\tfrac12$. The correction is **load-bearing**, not cosmetic: The theorem now bounds $④$ itself rather than $|④|$, and the sign of the quadratic term is exactly what decides whether a curvature term is needed — see Appendix C step 4.)* *(Label corrected in the same pass: the form printed is an intermediate-point identity, which needs $C^2$ regularity (H8); $\beta$-smoothness (H3) yields an integral-form remainder instead of a value at some $\xi$, so the earlier label cited the wrong assumption. The lemma is unused by Corollary 1 and Proposition 1 in any case, which use the defining strong-convexity inequality rather than a Taylor expansion — Appendix C step 3.)*
- **Lemma 5 (flatness–spectrum relation; not used by Corollary 1 or Proposition 1 — it is the measurement note of §4.2, and belongs to the flatness protocol and the diagnostic of Appendix J).** At a stationary point ($\|\nabla R_D(\theta)\|\approx0$): $\max_{\|\epsilon\|\le\rho} R_D(\theta+\epsilon)-R_D(\theta) = \tfrac12\rho^2\lambda_{\max}(H_D(\theta)) + o(\rho^2)$; at non-stationary points the read carries a first-order term $\rho\|\nabla R_D(\theta)\|$ (this is the measurement note of §4.2).
- **Remark 6 (former Lemma 6; PAC-Bayes source complexity).** The source-complexity term $C_2S_S$ is derivable via a PAC-Bayes argument but is deliberately not part of the theorem (see §4.2, first omission).
- **Lemma 7 (curvature transfer; H4; retained for the anisotropic remark of Appendix B and for the diagnostic of Appendix J — not used by the theorem).** $\lambda_{\max}(H_T(\xi)) \le \lambda_{\max}(H_T(\theta)) + \beta_H(\|\xi-\theta\|)$, hence the target–source spectral excess at matched points is bounded by $L''W_1$ (Lemma 2 raised one derivative order).
- **Lemma 8 (optimisation error to parameter distance; H9).** $\|\theta-\theta^*_S\| \le \sqrt{2\varepsilon^{\mathrm{pop}}_{\mathrm{opt}}/\mu_S}$.

**Small-shift condition (H10) — what it does and does not do.** H10, $W_1\le\mu_T r_T^2/(4L)$, is a *compatibility* condition between the shift scale and the growth scale of H5; it does **not** by itself establish that $\theta^*_S$ lies in the strong-convexity ball (a distant source well that is only $O(LW_1)$ worse is not excluded), so localization is stated as a separate assumption in Appendix C step 1, with a basin-separation certificate as a check. The displacement bound itself no longer depends on the $\alpha'$ bookkeeping at all: the sharp branch $L'^2W_1^2/(2\mu_T)$ follows from the strong-convexity inequality and the linear branch $2LW_1$ from Lemma 1 alone, and the $W_1^{3/2}$ estimate that the $\alpha'=1/2$ bookkeeping produced is withdrawn as dominated. H10 is therefore retained as a stated condition, not as a hypothesis the proof turns on.


# Appendix A-bis. The measurement-hierarchy proposition: derivation, regimes and falsification

> **Why this appendix exists.** The article states the proposition, the two regimes and the falsification
> condition, and points here for the derivation. This appendix is the removed detail: the second-order expansion
> and its assumption footprint, the two thresholds and what each one licenses, the placement argument, and what the
> statement does **not** claim. It is not counted against the article's page limit.

**The measurement-hierarchy proposition, stated so that it can be refuted.** The three readings above are instances of one statement, which we now make explicit rather than leave implicit, because a reviewer is entitled to ask what would have refuted it. Write $R_D$ for the risk of the loss on domain $D$ and $H_D$ for its Hessian in the parameters. Every quantity in the family is read by perturbing a released checkpoint: at a parameter point $\theta$, along a unit direction $u$ and at the **relative radius** the protocol fixes ($\epsilon=\rho\|\theta\|u$, Appendix M.1), the worst-direction increment is
$$\Delta_D(\theta,\rho,u)\;:=\;R_D(\theta+\rho\|\theta\|\,u)-R_D(\theta)\;=\;\underbrace{\rho\|\theta\|\,\langle\nabla R_D(\theta),u\rangle}_{\text{first order,}\;\propto\;\rho}\;+\;\underbrace{\tfrac12\rho^2\|\theta\|^2\,u^\top H_D(\theta+\tau\rho\|\theta\|u)u}_{\text{second order,}\;\propto\;\rho^2},\qquad \tau\in(0,1),$$
which is the ordinary second-order expansion to an intermediate point, an identity that needs $C^2$ regularity in a neighbourhood of $\theta$ and a bounded Hessian there (**H8** and **H6** in the notation of Appendix A) and no Lipschitz constant of the loss in the data — that is, **not H1**, which is what Corollary 1 uses and which plays no part here. Bounding the Hessian at the intermediate point by its value at the base point is a further step we do **not** take: what the two terms' ratio is governed by is stated at the base point, and it is one number,
$$r_D(\theta,\rho)\;:=\;\frac{\|\nabla R_D(\theta)\|}{\|H_D(\theta)\|\,\rho\|\theta\|},$$
the local slope measured in units of the local curvature scale at the operational radius. If $r_D\le\tfrac1{16}$ the quadratic term is at least eight times the linear one, so the read is dominated by curvature and its exponent in $\rho$ is $2$; if $r_D\ge1$ the linear term is at least twice the quadratic one, so the read is dominated by the gradient and its exponent is $1$, the two being equal at $r_D=\tfrac12$. The two regimes are separated by a band, not by a single threshold, and **the operational consequence is what matters here**: a perturbation-based diagnostic is readable as a curvature value only in a region where $r_D\le\tfrac1{16}$ (the small-$r_D$, curvature-dominated regime), and outside that region it is a sum in which the local slope is comparable with or larger than the curvature term.

**Statement.** Under **H6** and **H8** of Appendix A — a bounded parameter domain and $C^2$ regularity, in a parameter ball where the Hessian is bounded in operator norm and the radius fixed by the protocol is small against that bound — the read $\Delta_D$ is curvature-dominated only where $r_D(\theta,\rho)\le\tfrac1{16}$, and where $r_D$ is larger the read is dominated by, or comparable with, the local slope; so a finite-SGD checkpoint with a non-negligible residual gradient will generally produce a slope-dominated read, while the direction of comparison at any particular endpoint is a matter for measurement. **We do not measure $r_D$, and we say so rather than let the threshold read as a tested constant**: the numerator is a gradient norm at the fine-tuned endpoints, which this protocol does not record, so the placement of the measured cells is established by the two readings below and not by an evaluation of $r_D$. What the statement contributes is the **derivation of the two regimes and the judgement of which regime the ε-scaling reading can speak to**, not a measurement of the boundary between them; we therefore present it as a derivation with a measurement note attached, and not as a boundary we have located. We also do not claim that every fine-tuned endpoint of this study lies in one regime: non-stationarity is not by itself dominance, and the placement is reported as a measurement rather than argued from the checkpoint's provenance.

Three of our readings bear on that statement, and we report them as evidence about the placement rather than as illustrations of it. The **ε-scaling exponents of 0.56–0.81 (median 0.59)** are read at the two customary radii: they are well below the value $\approx2$ that curvature domination would require, so curvature domination is excluded there — with the qualification that these are effective exponents over a finite radius interval rather than the asymptotic exponent of either branch, and that at the third radius (0.01) the increments depart from the power law outright, which is why the protocol fixes the primary radius at 0.001. **That exclusion is the whole of what the first reading establishes, and it is a direct test of the regime**: an effective exponent near $2$ would place those cells in the curvature branch and would falsify the placement we report, on its own and without any further condition. The **SNR floor (18/18 cells $<2$, band 0.76–1.47)** is a second and independent obstacle, of a different kind: it is a failure of the gate for *using* the diagnostic as an outcome predictor, not evidence about first- against second-order, and the two must not be pooled into one argument. The **evaluator and reporting sensitivity** of §6(b) is a third and again independent obstacle: it is what a slope-dominated read does when the reference it is ratioed against is itself a trajectory quantity — the ranking flips with the evaluator, and in the single cleanest instance the sign of the reported gain flips with the **reporting column alone**, with runs, seeds and fine-tuning untouched. What we do not claim is impossibility: a larger gradient batch or a variance-reduced estimator changes the residual gradient that $r_D$ is built from, and with it the regime, as Appendix H.1 states; the statement is about this protocol and this estimator.


# Appendix B. Anisotropic curvature form

For anisotropic target curvature the isotropic factor $\lambda_{\max}(H_T(\theta))$ is replaced by the weighted alignment form; the steady-state gain of a prior of effective strength $\lambda$ reads
$$\Delta_\pi(\infty) \;\approx\; \lambda\,\frac{\mu_T}{\mu_S}\,\langle \nabla p_\pi, \Delta\rangle \;-\; \lambda^2\frac{\mu_T^2}{\mu_S^2}\|\nabla p_\pi\|^2 \;+\; \mathcal{O}(\lambda^3, \lambda^2\|\Delta\|),$$
with the weighted alignment $A_w$ replacing $\cos(\nabla p_\pi,\Delta)$; the isotropic special case (H7) recovers $A_w = A$ and the **schematic** Eq. (8) of §6.1 (labelled Theorem 3 in that theory supplement) **at leading order only — the second-order coefficient and the remainder differ between the two forms, as §6.1 states**. Signs are determined by the first-order term whenever $\lambda$ and $\|\Delta\|$ are small, which is the regime in which Theorem 3 is used.

The display moved here from §6.1 so that the article file carries only what it uses:

$$\Delta_\pi(\infty) \approx \lambda_{\max}(H_T)\Big[\tfrac{\lambda}{\mu_S}\|\nabla p_\pi\|\,\|\Delta(D)\|\,\angle(\phi_\pi,\phi_{\mathrm{shift}}) - \tfrac{\lambda^2\|\nabla p_\pi\|^2}{2\mu_S}\Big], \tag{8}$$



# Appendix C. Term-④ sensitivity: the sharp bound, the withdrawn interaction, and the algebra

Term ④ is the target-domain optimal displacement cost $R_T(\theta^*_S)-R_T(\theta^*_T)$. Write $\Delta:=\theta^*_S-\theta^*_T$ and $W_1:=W_1(\mu_S,\mu_T)$.

**Step 1 (Taylor expansion, Lemma 4).** There exists $\xi$ on the segment between $\theta^*_S$ and $\theta^*_T$ such that

$$|R_T(\theta^*_S)-R_T(\theta^*_T)|\le \left|\langle\nabla R_T(\theta^*_S),\Delta\rangle\right|+\tfrac{1}{2}\varrho(H_T(\xi))\|\Delta\|^{2},$$where $\varrho(\cdot)$ is the spectral radius.

The second-order sign here differs from Lemma 4 by design: Lemma 4 states the expansion *equality* ($-\tfrac12\Delta^{\top}H_T(\xi)\Delta$), whereas this step bounds that term in magnitude, using $|\Delta^{\top}H_T(\xi)\Delta|\le\varrho(H_T(\xi))\|\Delta\|^{2}$ (the same $\varrho$ as above), where $\varrho$ is the **spectral radius** (the largest $|\lambda_i|$; writing $\lambda_{\max}$ alone would be wrong wherever the Hessian has a negative eigenvalue of larger magnitude than its largest positive one, which is exactly the off-basin case this step is used for). The two forms are consistent; the appendix does not carry the pre-correction sign.

**Step 2 (first-order term bound, Lemma 2; inner-product form).** From the stationarity condition $\nabla R_S(\theta^*_S)=0$ and the gradient-domain KR duality, what the bound needs is the *inner-product* estimate, which **Appendix J.3 carries in full with the interior/constrained case split** (this step states the interior case only, where $\nabla R_S(\theta^*_S)=0$; the constrained case is the second branch of that split):

$$\langle\nabla R_T(\theta^*_S),\Delta\rangle\;\le\;L'W_1\|\Delta\|.$$

**No bound on $\|\nabla R_T(\theta^*_S)\|$ is used**: that quantity is controlled only in the interior case, where it equals $\|\nabla R_T-\nabla R_S\|$, so a norm-based chain would silently exclude constrained minimisers (Appendix J.3). This step replaced an earlier norm-based chain. **The first-order term of step 1 is therefore stated in the inner-product form** $|\langle\nabla R_T(\theta^*_S),\Delta\rangle|$, which is what this step bounds; a norm form would require the bound on $\|\nabla R_T(\theta^*_S)\|$ that the paper deliberately does not use, and the two steps would then not compose.

**Step 3 (displacement bound, Lemma 3).** Taking $\theta=\theta^*_S$ in the quadratic growth of H5, $R_T(\theta)\ge R_T(\theta^*_T)+\tfrac{\mu_T}{2}\|\theta-\theta^*_T\|^{2}$, and combining with Lemma 1 ($|R_T(\theta^*_S)-R_S(\theta^*_S)|\le LW_1$):

$$\|\Delta\|\le\sqrt{\frac{4LW_1}{\mu_T}}.$$

**Step 4 (curvature transfer, Lemma 7).** $\lambda_{\max}(H_T(\xi))\le\lambda_{\max}(H_T(\hat{\theta}))+\beta_H(\|\Delta\|+\|\hat{\theta}-\theta^*_S\|)$ (Weyl's eigenvalue perturbation inequality, standard; H4).

**Step 5 (combination; the term this step prints is withdrawn — see the retraction at the end of this appendix, and Eq. (5) is the live bound).** Substituting steps 2–4 into step 1, with $\|\Delta\|^{2}\le(4L/\mu_T)W_1$ — **the substitution is stated for the interior case**: Step 1 bounds the *absolute value* of the inner product while Step 2 supplies a *one-sided* bound, so the sign has to come from somewhere, and the interior case is where it does (the constrained case is the second branch of the case split in **Appendix J.3**, which is the live proof; the term printed below is withdrawn — see the retraction at the end of this appendix):

$$|R_T(\theta^*_S)-R_T(\theta^*_T)|\le 2L'\sqrt{L/\mu_T}\,W_1^{3/2}+\frac{2L}{\mu_T}\lambda_{\max}(H_T(\hat{\theta}))W_1+\mathcal{O}\!\left(\beta_H(L/\mu_T)^{3/2}W_1^{3/2}+\beta_H(2L/\mu_T)\|\hat{\theta}-\theta^*_S\|W_1\right).$$

Combining gives the pure-displacement term and the interaction term (the interaction term is given directly by $\lambda_{\max}(H_T(\theta))$ and no longer goes through the flatness-spectrum definition $S_T$; the spectral definition of $S_T$ is in the remark after Lemma 5):

$$\underbrace{2L'\sqrt{L/\mu_T}}_{C_4}\,W_1^{3/2}+\underbrace{\frac{2L}{\mu_T}}_{C_3}\,W_1\lambda_{\max}(H_T(\theta))+\text{curvature-transfer error}.$$

Here the interaction constant is $C_3=2L/\mu_T$ (after merging the transfer constants of Lemma 7) (see **Note C.1**), and the pure-displacement constant is $C_4=2L'\sqrt{L/\mu_T}$. The same two constants are what Steps 1–4 give directly: the first term of Step 1 is bounded by Step 2 with Step 3, and the second is $\tfrac{1}{2}\varrho(H_T(\xi))\|\Delta\|^{2}\le\tfrac{1}{2}\cdot\tfrac{4LW_1}{\mu_T}[\lambda_{\max}(H_T(\hat{\theta}))+\mathcal{O}(\beta_H)]$, so the appendix does not depend on the discarded fragment. ∎

> **Note C.1 — a corrupt source term, dropped rather than guessed.** The source document's trailing inline equation for $C_3$ is corrupt: it extracts as `C_3=2L/\mu_T rho^2)` with an unbalanced closing parenthesis, followed by a residual `mu_T)·(2/rho^2)` fragment of the withdrawn $S_T$-based form that has no left-hand side. The $C_3=2L/\mu_T$ shown above is read from the displayed combination equation and the paragraph's own running text; the $S_T$-residual has been **dropped rather than guessed**, and this note records the corruption instead of repairing it silently. **What can be added without guessing:** the discarded $\rho^{2}$ factor belongs to a *perturbation radius* that the withdrawn $S_T$-based form used and that Steps 1–4 do not use — with $\varrho$ the **spectral radius** of Step 1 and the Weyl bound of Step 4 supplying the $\lambda_{\max}$ correction, those steps fix $C_3=2L/\mu_T$ and $C_4=2L'\sqrt{L/\mu_T}$ on their own, so no coefficient printed above rests on the fragment.

The combination therefore yields the pure-displacement term $C_4W_1^{3/2}$ with $C_4=2L'\sqrt{L/\mu_T}$, and the interaction term $C_3W_1\lambda_{\max}(H_T(\theta))$ with $C_3=2L/\mu_T$. **The pure-displacement term is withdrawn**: it is never the lower envelope of Eq. (5)'s branches (**Appendix J.4**), and it is printed here only because this combination algebra is what the retraction concerns; the live bound is Eq. (5), whose quadratic branch carries $L'^2W_1^2/(2\mu_T)$.



# Appendix D. Pipeline and seed protocol rules

Dual-layer seed mechanism: the framework's `seed` argument is recorded in args.yaml, but the data-pipeline RNG does not consume it on these datasets (bit-identical replay); a `--shuffle-seed` CLI flag (deterministic permutation of the train split file order, validation untouched) restores seed validity — same value reproducible, different values provably different (controlled test). args.yaml does **not** record shuffle-seed; per-run registrations, with `train_obj` version numbers, are archived with this release. Pipeline-version rule: old/new pipeline mAP50-95 offsets measured 0.08–1.12 pp; every gain statement is same-pipeline paired; cross-pipeline numbers appear only in discovery narratives.

**Augmentation-RNG control (second seed layer, measured 2026-09-12).** A third seed layer exists and was quantified rather than assumed away: the released stack fixes the DataLoader generator (`manual_seed(6148914691236517205 + RANK)`), so with `--shuffle-seed` fixed the *augmentation* stream is bit-identical across runs and the registered σ sees data order only. A `--aug-seed` flag re-seeds the **worker-process** RNGs (random/numpy/torch) while leaving the generator, sampler, split-order permutation and initialisation untouched — augmentations change, nothing else does. Applied to SHWD→SFCHD at 100 epochs (20% budget, `--shuffle-seed 42` fixed), three augmentation seeds give baseline-arm test mAP50-95 of 43.810 / 43.930 / 43.800 (SD 0.072 pp) and strategy-arm (lr0.005) values of 44.500 / 44.350 / 44.020 (SD 0.246 pp), i.e. gains +0.690 / +0.420 / +0.220 pp against the matched same-budget baseline — all positive, mean +0.443 pp. The two arms were run on 4090s under ultralytics 8.4.120 [13] / torch 2.4.0+cu121 with identical `losses.py`/`modules.py` hashes and a verified-equal dataset file list; the anchor configuration reproduced the test endpoint to four decimals (mAP50 0.7371, mAP50-95 0.4450, Δ = 0.000 pp), which is the comparability check for this control and an independent reproducibility datapoint. Released: `a5_train_obj_aug.py` (trainer with `--aug-seed`), per-run `results.csv`/`args.yaml`.


# Appendix E. Reversal list and timeline

**Table T7.** The reversal list — five conclusions reversed by prospectively frozen rules and one further result invalidated for same-value duplication. The narrative, the triggers and the defensive rules are in E.1 below.

| # | conclusion reversed or invalidated | the reading it replaced | disposition | caught by |
|---|---|---|---|---|
| 1 | pipeline-pairing artefact | a "+0.80 pp steady-state gain" manufactured by a base-side pipeline effect of +1.12 pp | cell retired as an artefact | internal re-analysis |
| 2 | headline magnitude | quoted in turn as +0.62 pp → +0.40 pp → +0.45 pp → **+0.51 pp**, as the base was re-run and paired | corrected | internal re-analysis |
| 3 | alignment rank correlation | +1.00 | **−1.00** — the sign flips with the evaluator (§7) | internal re-analysis |
| 4 | loss-prior "positive tendency" | a single positive reading | dissolved into three zero/negative multi-seed estimates | internal re-analysis |
| 5 | historical module degradation | −10 pp | exposed as a silent mis-construction of the networks | checkpoint audit during internal review |
| 6 | same-value duplication (invalidated, not reversed) | a dead-layer insertion producing weights identical to the baseline | result invalidated | blinded external audit pass |
 Timeline exhibits: (i) s-OTDD measurement files predate all strategy-gain analyses (outcome-blind D); (ii) incident reports with their structural-audit evidence (checkpoint layer/parameter/loss triples; weight hashes); (iii) grading-document version history v13→v16.

## E.1 The reversal narrative, triggers and defensive rules (moved from §9.2)

Five conclusions were reversed by prospectively frozen rules during the study, and one further result was invalidated for same-value duplication (Table T7; Appendix E): a pipeline-pairing artefact that manufactured a +0.80 pp "steady-state gain" (base-side pipeline effect +1.12 pp); a headline magnitude corrected three times (+0.62 → +0.40 → +0.45 → +0.51 as the base was re-run and paired); an alignment rank correlation (+1.00 → −1.00) that flipped with the evaluator; a loss-prior "positive tendency" that dissolved into three zero/negative multi-seed estimates; a historical −10 pp module degradation exposed as a silent mis-construction of the networks; and a same-value duplication (a dead-layer insertion producing weights identical to baseline). In the 2026-09-11 campaign a **second, independent seed-replay instance** was caught before it could contaminate a paired comparison: three mendeley baseline runs nominally at seeds 42/43/44 have bit-identical epoch sequences (and one further run is a re-labelled copy), i.e. the `--shuffle-seed` injection had not taken effect for them. The screening rule introduced after the first replay incident — compare per-run epoch sequences by hash before forming any pair — is now mandatory; the affected runs are retained for the audit trail and re-run under new names (`_s43n/_s44n/_s45n`) rather than overwritten. Of the seven audit events, the dead-layer duplication was first flagged by a blinded external audit pass run on the draft (described below), and the module mis-construction by checkpoint audit during internal review; the remaining five were caught by internal re-analysis, and Appendix E lists the catcher of every event. **What the audit layer is.** It is a **blinded external audit pass** over the draft: the full draft, the grading table and the reference list are submitted to an independently hosted reviewing system that has no project background and no access to the repository, and its unedited responses are released with this submission. It is *external* in that the reviewing system is not author-controlled, and it is *not independent* in the sense of an unaffiliated human auditor: the authors chose the material and wrote the prompt, so its findings are advisory. Two assumption-level failures (the retracted family-control claim and the Appendix J.2 erratum) and the dead-layer duplication entered the trail through this pass, and every finding it raised was adjudicated by the authors, with rejections recorded alongside acceptances. The process therefore mandates, as its fourth rule, a "key assumptions × plausible ranges" sensitivity table at pre-registration time (Appendix G). We release the full trail — per-run results CSV, checkpoint layer/parameter/loss triples and weight hashes, versioned grading documents, the blinded audit prompts and their unedited responses, and the s-OTDD measurement files — because the reversals are the record of what the tests caught. That record is evidence about our *process*, not about the validity of the survivors: the evidence for the surviving claims is §8, and its limits are stated with it (§8.2, §9.3, §9.4).

**One correction is mathematical rather than empirical, and is recorded here for the same reason as the rest.** The interaction term $C_3W_1\lambda_{\max}(H_T(\theta))$ of the theorem has been **removed** (Appendix C step 5): term ④ is non-negative by target optimality, so the exact second-order identity bounds it by the first-order term alone once H5 is read as genuine local strong convexity, and the curvature contribution was slack. The correction was triggered by an objection raised in that external audit pass: the printed chain bounds the curvature magnitude by $\lambda_{\max}$, which is not a valid modulus for $|\Delta^\top H\Delta|$ whenever a negative eigenvalue exceeds $\lambda_{\max}$ in magnitude — i.e. precisely in the regime where a curvature term would be doing work. Both the objection and the re-derivation are part of the record; the directional object $\kappa^-_\Delta$ that a non-strongly-convex analysis would need is retained as a diagnostic, and the assumption whose use the correction turns on (that H5 is the two-point inequality rather than one-point growth) is now stated explicitly in Appendix G.

**Post-audit status of the surviving claims.** Three closure statements, each checkable against the released files. *(i) All cited geometry is canonical-protocol re-measurement, not legacy data.* The 30-epoch family was re-measured at all three radii under the canonical protocol on archived best checkpoints; the legacy flatness corpus is not merely imprecise but internally inconsistent — the same checkpoint recorded as 5.19×10⁵ under the legacy protocol reads 342.3 under the canonical one — so no legacy flatness reading is used anywhere in this paper. Every geometric number cited comes from the canonical re-measurement, and legacy values appear only inside the retraction of Appendix J.2. *(ii) All outcome claims are post-repair, same-pipeline and paired.* Every gain statement in §8 comes from runs made after the `--shuffle-seed` repair and is paired against a same-family, same-budget baseline; cross-pipeline readings survive only in discovery narratives and are marked as such. The pipeline offset is bounded empirically rather than assumed: re-running the 20% label fraction under the current pipeline reproduced the two registered *single runs* to within 0.01 pp on the baseline and exactly on the strategy arm: the released runs `shwd2sf_base100_s42n` and `shwd2sf_lr005_100ep_s42n` read 0.4396 and 0.4426 against the registered 0.4397 and 0.4426 (the ten-seed cell means are 0.4386 and 0.4440). This is a single-run reproduction of two named runs, not a reproduction of the cell means. *(iii) No surviving claim depends on a withdrawn cell.* Of the audit events above, one cell was retired as a pipeline-pairing artefact, one magnitude was corrected, and one cell is retained only as a retraction; the criterion-passing cells, the dose–response, label-budget and control readings, and the within-domain damages were all produced after the repairs. This is a statement about provenance, not a claim of completeness: we can show that the survivors were re-measured under the repaired protocol, and we cannot show that the repaired protocol is free of defects of a kind we have not yet imagined — which is why every surviving claim is stated together with the measurement that could overturn it.


## E.2 The selection premium: per-cell restatements and the cells the coincidence affects (moved from §8.6)

**The premium was measured per cell; the measurement and its direction are reported in the companion paper on evaluation validity rather than here** — that paper owns the per-cell and per-arm values, the endpoint restatements, and the enumeration of which cells the `val`/`test` coincidence affects. What this paper retains is the contrast that conditions its own headline numbers: the published-protocol magnitudes **+1.76 pp** (smoke→SFCHD) and **+0.54 pp** (SHWD→SFCHD) are best-checkpoint levels on the split that selected them, not held-out test estimates. **The clean three-way protocol and its disclosures.** For the affected cells a three-way protocol (label subset / validation carve-out from the remaining training pool / untouched test split) removes the structure, and we report it rather than merely proposing it: on the clean protocol both headline cells hold — smoke→SFCHD **+1.434 pp at ten seeds** (baseline 42.062 → strategy 43.496; SD 0.383 pp; paired t = **11.84**; sign-flip permutation p = **0.0020**, the n = 10 floor, all ten seeds positive) and SHWD→SFCHD **+0.507 pp** (43.559 → 44.066; SD 0.488 pp; t = **3.29**; p = **0.0098**, nine of ten positive) — and these, not the published-protocol values of §8.3, are the paper's primary readings of the two headline cells. **The eleven- and thirteen-seed extension, on which the family-level status below rests:** smoke→SFCHD **+1.409 pp** (baseline 42.108 → strategy 43.517; SD 0.372 pp; paired t = **12.55**; permutation p = **0.000977**, the n = 11 floor, eleven of eleven positive) and SHWD→SFCHD **+0.628 pp** (43.484 → 44.112; SD 0.489 pp; t = **4.63**; p = **0.001221**, twelve of thirteen positive). **The extension moved the point estimate by −0.025 pp and +0.121 pp on the two cells** — it tightened the interval rather than raising the effect. **At ten seeds neither clean-tier test clears the paper's own roster-wise correction** (q = 0.052 and 0.127); **extended to eleven and thirteen seeds both clear it (q = 0.0159), and that extension postdates the ten-seed values** (**Appendix F.1**): what the clean protocol buys is the removal of the checkpoint-selection coincidence, not additional multiplicity protection. Three disclosures attach. First, the clean-protocol magnitudes are lower than the published-protocol ones they replace as evidence (+1.434 vs +1.76; +0.507 vs +0.54), which is the selection premium of this section working at cell level. Second, within the clean protocol the estimate **shrank as seeds were added**: +1.562 / +0.693 pp at six seeds, +1.420 / +0.492 at nine, +1.434 / +0.507 at ten, the direction selection inflation predicts, which is why the ten-seed value is the one we report. Third, the protocol is released as `*_3way.yaml` with its deterministic carve rule (seed 42 from pool-minus-subset) and a zero-intersection check on all three pairs at file-name level (Appendix D). The visdrone→dota15 probe, the third cell the coincidence affects, has no clean-protocol counterpart in this release, and we do not claim the published protocol is equivalent to the clean one. Image-level overlap between the MAFA source and the mask target is negligible (pHash 0.06%). **Incidental audit note carried with this block** (the placeholder sentence the moved text relies on): the anchor run of the 2026-09-11 campaign reads **Δ = 0.000 pp**, and in that campaign three mendeley baselines are bit-identical across seeds (§8.6, §9.2).

## E.3 Framing removed from §1 on compression

**The observed-pattern list removed from the opening paragraph of §1 (motivation only; each item is stated where it is graded).** Verbatim: “Practitioners observe patterns none of these accounts predicts on its own: a larger learning rate helps early and hurts late; a loss function that wins on one domain pair loses on another; attention modules that help in-domain do nothing cross-domain; and two metrics of the same model can disagree about whether a strategy ‘worked’.” Where each pattern is graded in the main text: the learning-rate pattern by the two cells of C2 (§5.2, §8.3), whose generalisable form is tested in a companion paper; the loss-function pattern by the loss-prior null (§8.4); the attention-module pattern by the structure-module block (§8.4, Appendix K.2); and the metric-disagreement pattern by §8.5 and by the dual-metric paragraph of §1. **Also compressed in the same paragraph (wording only):** “optimal-transport bounds that charge an additive shift cost; flatness-based bounds that charge for fragile geometry; and optimisation theory that prices the training budget” became “transport bounds that charge for shift, flatness bounds that charge for geometry, and optimisation theory that prices the budget”, with the lead-in replaced by the closing clause “none of which predicts the patterns practitioners report”. Both accounts remain: the three-account framing, the acute-problem sentence and the object-detection setting are unchanged.

## E.4 The premium enumeration in full (moved from §8.6, 2026-09-19)
**The premium's per-cell and per-arm measurement, and the endpoints that no selection can touch, belong to the companion paper on evaluation validity rather than here** — that paper owns the premium's analysis; this paper retains only the two published-protocol magnitudes as the contrast that conditions its own headline numbers. Unfavourable, and decisive for how the numbers must be described: **the levels this paper reports are best-checkpoint levels on the split that selected them**, not held-out test estimates, so +1.76 pp and +0.54 pp are selection-selected magnitudes and the arm plateau is a different (here larger) quantity. Both readings hold together and we give both. The seed trajectory under the clean protocol, and the released analysis (`selection_premium.py`), are in **Appendix E.2**; the per-cell restatements and the enumeration of the cells the `val`/`test` coincidence affects belong to the companion paper rather than here (Appendix E.2). **Primary readings of the two headline cells, under the clean three-way protocol, in **mAP50-95** (built 2026-09-14, after selection and before any clean-protocol run — Appendix M.3):** smoke→SFCHD **+1.434 pp** at ten seeds (baseline 42.062 → strategy 43.496; SD 0.383 pp; paired t = **11.84**; paired sign-flip permutation p = **0.0020**, the n = 10 floor, ten of ten seeds positive) and SHWD→SFCHD **+0.507 pp** (43.559 → 44.066; SD 0.488 pp; t = **3.29**; p = **0.0098**, nine of ten positive), with the published-protocol values reported beside them as the selection-premium comparison. **The extension this status is computed from, printed here so the arithmetic can be checked against the reading it acts on:** smoke→SFCHD **+1.409 pp at eleven seeds** (42.108 → 43.517; SD 0.372; t = **12.55**; p = **0.000977**, eleven of eleven positive) and SHWD→SFCHD **+0.628 pp at thirteen seeds** (43.484 → 44.112; SD 0.489; t = **4.63**; p = **0.001221**, twelve of thirteen positive), the point estimate moving by −0.025 and +0.121 pp respectively. **These are cell-level tests, and we state their family-level status here rather than only in the discussion: under this paper's own roster-wise convention they do not clear the correction at ten seeds (q = 0.052 and 0.127) but do clear it at the eleven- and thirteen-seed extension (q = 0.0159; §9.3, Appendix F.1), the ten-seed miss being the coarse 2/2¹⁰ floor rather than weak evidence; that extension postdates the ten-seed values, so the family-level statement this paper makes remains the cell-level reading above, with the passing value reported under that provenance.**

## E.5 Assigner-level OOM fallbacks: the audit, and the runs removed and replaced (2026-09-26)

**Why this appendix exists.** Ultralytics catches a CUDA out-of-memory error inside the task-aligned assigner and **silently falls back to CPU for that batch**; the run continues, the epoch completes, and the reading is written. It is therefore invisible in the summary statistics and had to be found by scanning the logs. This appendix records the audit and every run that was removed.

**The scan.** Every training log of every campaign batch on the experiment host was matched against the exact fallback signature `CUDA OutOfMemoryError in TaskAlignedAssigner` (a bare `OutOfMemoryError` pattern was rejected as a false-positive source: the guard script's own comments contain it). The scan covers 507 run directories and their lane-level and per-run logs.

**Three findings.** (i) **The trigger is the corpus, not the run.** Fallbacks occur only on the dense aerial corpora — DOTA15, AI-TOD and VisDrone, where a single training batch can carry several thousand instances (the worst observed batch had 3,927) — and never on the helmet, smoke, mendeley, MAFA or `sns` corpora, whose busiest images carry about a dozen boxes. On the two SFCHD cells that carry this paper's graded results the fallback count is **zero**. (ii) **On any one run the effect is not measurable.** A cell-wise paired comparison, affected against unaffected runs of the same cell, gives a median mAP50-95 difference of **−0.0006 pp** (mean −0.0010 pp) over 20 cells, against the data-order σ̂ of **0.166–0.190 pp** — one third of the noise floor or less. The mechanism explains the size: the fallback is an isolated single batch, the next batch returns to GPU, and the checkpoint this paper reports is selected as a maximum over epochs. (iii) **It is a concurrency artefact, and it was removed at the source.** A schedule that ran more than one training process per device pushed a 24.5 GB card to 23.9 GB and produced **37–59 fallbacks in a single run**; a single-process-per-device schedule produced **zero fallbacks in all 33 runs** it launched, at the same settings. The per-run VRAM gate that the earlier queue relied on (≥ 18 GB free) is insufficient, because 18 GB is enough for one process at a 21.3 GB peak but not for two: the property that matters is *exclusivity of the device*, which a free-memory threshold cannot express.

**Runs removed and replaced.** All of them were re-run under the single-process schedule; every replacement returned a clean log (zero fallbacks) and is the value now reported.

| removed run | reason | replacement |
|---|---|---|
| `vis_d15_base100_s54n` | fallback in the **validation** pass | re-run, clean, in the CSV |
| `vis_d15_lr005_100ep_s54n` | fallback in the **validation** pass | re-run, clean, in the CSV |
| `d15_ai_lr005_100ep_s50n` | fallback during training | re-run under the dispatcher |
| `r15b_y11_aitod_base100_s45n` | fallback during training, killed at epoch 0 | re-run, clean, in the CSV |
| `r15b_y11_aitod_base100_s46n` | partial attempt from the concurrent window | re-run, clean, in the CSV |
| `d15_ai_base100_s50n` | 59 fallbacks (concurrent window) | re-run, clean, in the CSV |
| `d15_ai_base100_s51n` | killed at epoch 18 by the schedule change | re-run, clean, in the CSV |
| the 18 `_oomfix` replicas | archived-campaign runs whose logs show a fallback | re-run under the dispatcher; all 18 clean |

**What this does not claim.** The archive is not entirely free of the fallback: runs of the earlier campaigns whose logs show one are listed above and have clean replicas, but this paper does **not** re-analyse every archived reading, because the paired comparison of (ii) shows the effect to be below the noise floor in every cell where it was measured, and the corpora that carry the graded results are unaffected. Replicas were written under new names (`*_oomfix`) so that **no published reading was overwritten**; both the original and the replica are on disk, and the replica is the one this paper reports. The schedule and the log scanner are released with the manuscript.

# Appendix F. Number freeze table (v16) and sensitivity


**Null exceedance of the frozen rule (derivation).** Write the pass condition as $\overline{\Delta} > 3\hat\sigma_{\rm strategy}$ with $n = 3$ paired seeds. Under the null $\overline{\Delta} \sim N(0, \sigma_d^2/n)$, and $\hat\sigma_{\rm strategy}/\sigma_{\rm strategy} = s$ is independent of $\overline{\Delta}$ (mean and variance of a normal sample are independent), with $2s^2 \sim \chi^2_2$, i.e. density $f(s) = 2s e^{-s^2}$. Hence, with $q = \sigma_d/\sigma_{\rm strategy}$, $$P_{\rm null}(q) = \int_0^\infty 2s e^{-s^2}\Big[1 - \Phi\big(3\sqrt{3}\,s/q\big)\Big] ds,$$ which has two limits that matter more than the interior values, and neither is small: $P_{\rm null}(q) \to \tfrac12$ as $q \to \infty$ — when the paired noise swamps the strategy-side σ̂ the threshold becomes negligible and the rule degenerates towards a coin flip — and $P_{\rm null}(q) \approx q^2/54$ as $q \to 0$ (numerically $1.66\times10^{-3}$ at $q = 0.3$ against $q^2/54 = 1.67\times10^{-3}$). *The rate is set by the σ ratio, not by the rule*, and for large-$q$ cells the rule is close to vacuous, which is why the secondary statistics rather than the criterion carry the inference there. An earlier version of this appendix printed a large-$q$ form that *decreased* in $q$; it matched no column of the table below and is corrected here. Numerically (closed form and a paired-arm Monte Carlo with $1.5\times10^6$ draws agree to three decimals; released script `null_exceedance.py`):

| q | 0.6 | 0.8 | 0.9 | 1.0 | 1.2 | 1.4 | 1.6 | 2.0 | 2.5 |
|---|---|---|---|---|---|---|---|---|---|
| per-cell null exceedance | 0.65% | 1.14% | 1.44% | 1.75% | 2.47% | 3.28% | 4.16% | 6.08% | 8.66% |
| expected null passes in 26 configurations | 0.17 | 0.30 | 0.37 | 0.46 | 0.64 | 0.85 | 1.08 | 1.58 | 2.25 |
| P(at least one null pass) | 15.7% | 25.9% | 31.3% | 36.9% | 47.8% | 57.9% | 66.9% | 80.4% | 90.5% |

The family rows are computed on the 26-configuration enumerated roster used everywhere else in this paper (§8.2, Appendix I), not on the recorded count of 28; the quoted range (0.37–1.65 expected passes, 31–82%) is **derived from the null model rather than measured**, and spans the q values the graded cells actually realise (q ≈ 0.9–2.1), and is the same arithmetic restricted to that sub-range. Two corrections are recorded here rather than silently applied: an earlier printing of this table used the 28-cell denominator for both family rows (0.40–2.42; 33.3–92.1%), which contradicted the roster rule stated in §8.2; and its q = 0.6 column of the family-wise row read 9.7% where the closed form and the Monte Carlo both give 16.8% on 28 cells (15.7% on the 26-configuration roster). The per-cell column was unaffected and reproduces to three decimals against a paired-arm Monte Carlo with $1.5\times10^6$ draws.

The family is therefore *not* protected by the rule at any plausible q, and the tier structure (ten-seed replication extension, permutation tests, FDR robustness read of §9.3) carries the inferential weight.

Canonical anchors as listed in the grading table v16 (§ Anchors). Sensitivity: the corroborating cell’s strategy-side σ̂ is 0.166 pp at ten seeds (0.13 pp at the registered three seeds; σ̂ CI [0.69×, 1.83×] at n = 10), and the strong cell’s is 0.190 pp (CI [0.131, 0.347]). At the ten-seed σ̂ upper bound the corroborating cell falls to 1.8σ on the strategy-side rule while its paired test (t = 9.35, p = 6.2×10⁻⁶) and exact permutation p (1.1×10⁻⁵) are unaffected — both conventions are reported for every passing cell rather than averaged. **The σ-convention, stated in full here because the main text carries it in compressed form (§9.3).** The paired-difference σ measures the contrast's total noise and is the scale an NHST decision on the paired difference would use; the strategy-side σ measures whether the *strategy's* gain replicates across seeds, which is the reproducibility question this paper asks — so the criterion's frozen choice follows the question rather than the test. At three seeds the strategy-side σ̂ CI is [0.5×, 6.3×], at which both cells fall below the 3σ line (disclosed rather than averaged away), and the ten-seed extension tightens it to [0.69×, 1.83×]. Assumptions×ranges table: see Appendix G. Additional anchors frozen on 2026-09-11: dose–response 30 ep +0.86/+0.87/0.00/−0.76 pp and 100 ep +0.07/+0.29/+0.53/−0.38 pp at 2.5×/5×/10×/20×; label-budget baselines 0.4128/0.4397/0.4502/0.4632 with strategy gains +0.51/+0.29/+0.70/+1.25 pp at 10/20/30/50%; controls cosine +0.12/+0.16 pp, frozen backbone −4.94/−3.95 pp, AdamW +0.33/+0.31 pp; 200-episode baseline 0.4385 (early-stopped) vs lr0.005 +0.52 pp; within-domain dota15 +1.12/+0.95/+0.93 pp; pre-training far-field reads (ρ = 0.01): SHWD→SFCHD 7,334, MAFA→mendeley 2,534, mendeley→mendeley 323, dota 297, visdrone 283, firesmoke 207, mask 59,248.
## F.1 Multiplicity: units, p-value set and sensitivity to the family definition (moved from §8.2)

**The 3-vs-3 defence chain, in full (recomputed, not transcribed).** Where a tier is carried by three
seeds per arm, the complete-separation event and its null probability are reported together, so that
the separation cannot be read as stronger than it is: the corroborating cell's corroborating tier has
complete separation **0.21 pp**, and under permutation the 3-vs-3 complete-separation null probability
is **$2/\binom{6}{3}=2/20=0.10$ two-sided** (**0.05 one-sided**) — the same two-sided convention used for
the paired sign-flip floors above. Complete separation at three seeds is therefore a weak event on its
own, and the tiers that carry inference are the paired tests, not the separation.


**Seed-σ composition (moved from §9.4).**

The augmentation-RNG component has since been **measured on the strong cell as well** (smoke→SFCHD, 100 epochs, 20% budget, `--shuffle-seed 42` fixed, `--aug-seed` 101/202/303): the baseline arm reads 0.4230 / 0.4250 / 0.4270 and the strategy arm 0.4410 / 0.4410 / 0.4370 on the target test split, i.e. gains of **+1.80 / +1.60 / +1.00 pp (mean +1.47 pp, 3/3 positive, paired t = 6.10)**, with endpoint SDs of 0.20 pp (baseline) and 0.23 pp (strategy). That is the *same order* as the corroborating cell's augmentation component measured above, so on the strong cell the gain is not an artefact of the augmentation stream either.
 Three components have now been separated by direct measurement on the same cell (SHWD→SFCHD, 100 epochs, 20% subset). (i) *Training-split order*, which is what the registered σ varies (0.18–0.21 pp paired-difference, §8.2). (ii) *Augmentation RNG*, measured with three worker-process seeds while the DataLoader generator, the split-order seed and the initialisation are held fixed: strategy-arm SD **0.246 pp**, baseline-arm SD **0.072 pp**, i.e. 1.07–1.89× the registered σ, which makes the 3σ rule *more permissive* than its nominal calibration; the strong cell's margin absorbs this while the corroborating cell clears the registered threshold and not the augmentation-inflated one, so that cell is carried by its conventional statistics (§8.2, §8.3). The rule is **not** recalibrated for this — the shortfall (1.07–1.89×) sits below the 3× trigger set before the measurement (Appendix G) — so the two statements are complementary rather than in conflict: the line stands, *and* this one cell is carried by its conventional statistics instead of by it. (iii) *Initialisation*, measured by training the source endpoint from scratch three times and re-running both arms from each: gain SD **0.146 pp** (3/3 positive, mean +0.437 pp) and absolute-endpoint SD **0.209 pp**. **Seed-count convention for this appendix: every component above is estimated at n = 3.** Where a σ̂ is also quoted at ten seeds (§8.2), the two estimates are not interchangeable, and each comparison in this appendix names the one it uses. Every component therefore rests on three seeds, and on these readings the **largest is the augmentation component** (0.246 pp), with the data-order component the registered design does measure next (0.18–0.21 pp) and the initialisation component smallest (0.146 pp); what matters for the headline cells is that none of the three is large enough to manufacture an effect of ≈1.4–1.8 pp. The controls cover one cell, one pair and one budget.

**Family-level analysis: the three family definitions (moved from §9.3).** **Family-level analysis, reported as robustness rather than as a family-wise guarantee: paired tests with BH-FDR (q = 0.05) over the 26-configuration roster**, given three ways because the family choice is not innocent and because the roster was enumerated after the outcomes. (i) The two extended *family* arms, the remaining 24 roster configurations entering at p = 1 (m = 26, the Appendix I roster): q = 1.7×10⁻⁸ (smoke→SFCHD), 8.1×10⁻⁵ (SHWD→SFCHD). (ii) The three extended arms alone (m = 3): q = 6.2×10⁻⁶ and 9.6×10⁻¹⁰ for the two family arms. The family-external visdrone→dota15 arm is not one of the two extended *family* arms — "family member" here means a member of that extended-arm set, not a row of the 26-configuration roster (its configuration is row 4 of Appendix I) — so its raw p = 1.7×10⁻¹³ is the primary number we report; for completeness, including it in that m = 3 completion would give q = 5.0×10⁻¹³. (iii) The two family arms without completion (m = 2, listed p-values): q = 1.3×10⁻⁹ (smoke→SFCHD) and 6.2×10⁻⁶ (SHWD→SFCHD). Every family-level value survives by orders of magnitude. It is nonetheless a *robustness read, not a family guarantee*: the extension was triggered by the screening outcome, so correcting within the selected arms cannot control the FDR of the family that generated the selection, and the conventional analysis does not rescue the registered tier either (BH q = 0.29 and 1.00 at three seeds) — hence the frozen criterion is called the *screening* instrument and the tier structure carries the inference. At three seeds the same procedure is not decisive (paired p = 0.011 does not survive the correction; Welch p = 0.0008 does). The two σ̂ conventions also diverge at ten seeds: the strong cell remains at 5.1σ while the corroborating cell falls to 1.8σ on the strategy-side rule (its 10-vs-10 two-sample permutation p = 1.1×10⁻⁵ (paired sign-flip floor $2/2^{10}=2.0\times10^{-3}$) and its paired test are unaffected by the σ̂ convention). **Fresh-seed check.** Restricting the extension to the seven seeds that were *not* part of the screening reading leaves the three gains intact: +1.75 / +0.55 / +3.60 pp for smoke→SFCHD / SHWD→SFCHD / visdrone→dota15 (paired t = 26.50 / 9.50 / 48.71; p = 1.9×10⁻⁷ / 7.8×10⁻⁵ / 5.0×10⁻⁹; strategy-side effects 9.3σ / 3.0σ / 26.6σ; exact 7-vs-7 two-sample permutation p = 5.8×10⁻⁴ — the complete-separation value, with paired sign-flip floor $2/2^7=0.016$ — in all three). The replication therefore does not rest on the three seeds it reuses, and the corroborating cell in particular is carried by fresh data alone (released script `fresh7_seed_analysis.py`). "Not detected" is a power statement, not evidence of absence, and the power is quantified rather than asserted: with the observed paired-difference σ (0.18–0.21 pp) a three-seed paired test reaches 80% power only at 0.56–0.62 pp, a ten-seed test at 0.18–0.21 pp; and the frozen criterion's *expected* threshold $3\mathbb{E}[\hat\sigma_{\rm strategy}]$ is 0.35–0.61 pp at three seeds and 0.38–0.67 pp at ten seeds for the σ̂ values in play (0.13–0.23 pp). Hence the negative results of §8.4 read "no gain ≥ +0.4 pp was detected", not absence of effect: below roughly half a point the registered design cannot see, and the +0.4 pp reading line sits at that boundary by construction (released script `conditional_and_power.py`). Fisher-combination and Bayesian effect-size treatments are provided in Appendix H as secondary views.

**What the multiplicity family is, and how sensitive the correction is to its definition.** The BH correction is applied to *configurations*, not to arms: the unit is one (source endpoint → target corpus, budget) configuration, tested by the paired contrast between its registered strategy arm and its baseline, and the other 24 configurations of the roster enter with p = 1 because they carry either a single arm or no paired seeds — an after-the-fact sensitivity convention rather than a prospectively defined family. The p-value set actually entering the correction is therefore two values, 0.011 and 0.081 at three seeds (and 6.4×10⁻¹⁰ / 6.2×10⁻⁶ at ten seeds; 1.9×10⁻⁷ / 7.8×10⁻⁵ on the fresh seven). Sensitivity to the family definition, since the unit choice is not innocent: over the **26-configuration roster** (Appendix I) the ten-seed values are q = 1.7×10⁻⁸ / 8.1×10⁻⁵; over the **recorded registry count of 28** they are 1.8×10⁻⁸ / 8.7×10⁻⁵; and over the **arm-level count of 138 contrasts** in the roster they are 8.8×10⁻⁸ / 4.3×10⁻⁴ — every version clears by orders of magnitude, and none of them rescues the registered three-seed tier (q = 0.29 / 0.31 / 1.00 across the three family definitions). All three variants are recomputed under one stated convention — two real paired tests, every other configuration entering at p = 1 — by the released script `recompute_family_sensitivity.py`; the values previously printed for the 28- and 138-variants were not derivable from BH under that convention and are corrected here. **The clean-protocol tier under the same convention, stated because it does *not* pass.** The three-way replication of §8.6 gives the two headline cells p = 0.0020 and 0.0098; under the identical roster-wise convention (m = 26, every other configuration at p = 1) those become **q = 0.052** and **q = 0.127** at ten seeds — **neither clears q = 0.05**, and the first only because 26×(2/2¹⁰) = 0.0508, i.e. because the permutation floor is coarse at n = 10 rather than because the evidence is weak — and **q = 0.0159 for both** (= 26 × 0.001221 / 2, rank 2 of 26) once the two cells are extended to eleven and thirteen seeds, which clears. That extension postdates the ten-seed values, so the caveat above applies to it verbatim. The clean tier is therefore not presented as surviving a family-wise correction, and the division of labour of §8.2 applies to it unchanged: within-cell paired tests carry the inference and every family-level read, in either protocol, is reported as robustness. What the clean protocol buys is the removal of the checkpoint-selection coincidence (§8.6), not additional multiplicity protection. **Why the frozen rule is kept despite carrying no family control.** It is retained because it was frozen before the headline cells' final completions, because it — not the conventional tests — selected the arms that were later extended (so removing it would erase how the extension came about), and because its null behaviour is derived rather than assumed (Appendix F). It is not retained as evidence: the abstract, §9.3 and §10 state that inference rests on the fresh-seed paired tests and the cell-level ten-seed tests, with the family-level correction reported as robustness, and the rule enters the paper only as the screening instrument. **What σ covers — measured, not asserted.** The registered σ varies the training-split *order* only: initialisation is fixed, and in the released 8.4.120 stack the data-pipeline RNG does not consume the framework seed (Appendix D). The excluded component was therefore measured directly rather than declared. Re-running the same cell (SHWD→SFCHD, 100 epochs, 20% budget) with three *augmentation-RNG* seeds — worker-process RNG only, data-order seed and initialisation held fixed — gives a strategy-arm SD of **0.246 pp** and a baseline-arm SD of **0.072 pp** (per-seed gains +0.69 / +0.42 / +0.22 pp, 3/3 positive, mean +0.443 pp; §8.3). The augmentation component is thus **1.07–1.89×** the registered data-order σ (0.13–0.23 pp): the registered σ is a *lower bound*, so the 3σ rule is **more permissive** than its nominal calibration, not less. We state the consequence for the cell it affects rather than for the paper as a whole. The strong cell is unaffected: its +1.76 pp gain clears 3σ̂ = 0.57 pp on the registered ten-seed σ̂ = 0.190 pp and 3 × 0.246 = 0.74 pp on the augmentation-inflated σ. The corroborating cell is **not** unaffected, and the honest reading is that it is convention-dependent: its +0.54 pp gain clears 3σ̂ = 0.50 pp on the registered data-order σ̂ = 0.166 pp, and falls below 3 × 0.246 = 0.74 pp once the measured augmentation component is included. What carries that cell is therefore its *conventional* statistics — paired t = 9.35 (p = 6.2×10⁻⁶) at ten seeds and +0.55 pp on the seven fresh seeds (p = 7.8×10⁻⁵), neither of which uses σ — and its criterion pass is reported as conditional on the data-order σ convention. This is a disclosure against interest and we make it explicitly: the measured lower-bound shortfall is not large enough to require recalibrating the 3σ line or the +0.4 pp module threshold for the family (1.07–1.89×, below the 3× trigger set before the measurement), but it is large enough to move the one cell whose margin was ≈1.1× the line. An anchor run of the identical configuration (`--aug-seed 101`, same shuffle seed and pretrain) reproduced the test endpoint to four decimals (Δ = 0.000 pp), so this axis does not enter the comparison. (The three headline arms were later re-tested under the same rule with ten seeds per arm in a pre-specified extension — plan timestamped before the extension data existed; the registered 3-seed readings remain the graded values and the extension is reported alongside them, §5.2.) We call that extension the **replication tier**, not a confirmatory one: the arms extended are the arms that passed screening, and the ten-seed tests reuse the three screening seeds (seven paired differences are fresh, three are not). The fresh-only analysis is reported in §5.2 and is the form of the replication reading that carries no reuse. *Freezing timeline (stated precisely).* Blinded dual-model predictions were written before any outcome data existed (2026-09-02, repository-timestamped). The grading rules themselves — the domain-stratified noise thresholds, the 1.5σ single-run and 3σ three-seed-mean rules, and the strategy-side σ convention — were fixed in the internal grading documents of 2026-09-04/05 and re-stated on 2026-09-07: i.e., after the first same-pipeline observations of the headline cells but before their final 3v3 completions, and never changed after those completions. A fully outcome-blind pre-registration was therefore not achieved for the rule-freezing step, and we do not claim one; "prospectively frozen" (shorthand "frozen") is the accurate label for what was achieved, and it is used throughout — the unqualified term "pre-registered" is avoided for the rule-freezing step. One rule-level claim made at registration — that the 3σ rule carries its own family control — was later retracted (§8.2) and is recorded in the audit trail. The criterion is an effect-size rule, not an NHST test: σ is estimated from the same three seeds that grade the cell, so the rule has no fixed level — its per-cell null exceedance is a function of $q = \sigma_d/\sigma_{\rm strategy}$ (the paired-difference σ over the strategy-side σ̂). In closed form (derived in Appendix F) the exceedance is 0.7% at q = 0.6, 1.4% at q = 0.9, 1.8% at q = 1.0, 3.3% at q = 1.4, 6.1% at q = 2.0 and 8.7% at q = 2.5; the two criterion-passing cells sit near q ≈ 0.90 (smoke→SFCHD, 1.4%) and q ≈ 1.4–2.1 (SHWD→SFCHD, 3.3–6.4%, the range reflecting whether the three-seed or the ten-seed paired-difference σ is used). Earlier versions quoted a flat ≈1.7% for this quantity, which is correct only near q ≈ 1 and understates the cells we can calibrate. **The rule therefore does not by itself control family-wise error**: at the observed q values the expected number of null passes among the enumerated family cells is 0.37–1.65 and the probability of at least one is 31–82%. The count distribution matters more than its mean, because two cells is what we observe: under the global null, and on the enumerated roster adopted below, the probability of *at least two* passes is 5.3% at q = 0.9, 7.6% at q = 1.0, 20.9% at q = 1.4 and 49.7% at q = 2.05 (one or more: 31 / 37 / 58 / 82%). A two-pass screening outcome is therefore not by itself evidence against the null, and we do not present it as such. What the screening cannot supply, the conditional step can: *given* that these two arms were the ones taken forward, the probability that both would clear their paired test at ten seeds under the null **if the two cells' tests were independent** is $6.4\times10^{-10} \times 6.2\times10^{-6} = 4\times10^{-15}$ — and they are not independent, since the two cells share the target corpus, the target label subset and the pipeline, so this product is an *illustrative* joint bound under an assumption the design violates rather than a calibrated joint probability; the quantity that carries inference is each cell's own paired test, with the family-level correction reported separately, and $1.5\times10^{-11}$ on the seven fresh seeds alone — the subset that is independent of the screening that performed the selection. Because the selection was made on the screening reading, we state that second quantity as *conditional*, not as a family-level guarantee (released script `conditional_and_power.py`). This is why every passing cell carries its full secondary statistics (paired t, Welch, permutation, BH-FDR) and its defence chain, disclosed alongside — grading never rests on the criterion alone. σ is a (strategy × domain-pair) property (Table T8: shwd2sf base 0.18 / lr005 0.13; smoke2sf 0.25/0.23; mende sns 0.26 pp), with the n = 3 sd estimation CI ([0.5×, 6.3×]) disclosed. **What a "seed" varies here.** A seed in this study varies the *presentation order of the training split* (the shuffle-seed permutation of Appendix D); the pretrained initialisation is a fixed checkpoint, and on these datasets the framework's own seed argument is not consumed, so augmentation randomness and framework-level RNG are identical across runs. The reported σ (0.13–0.26 pp) is therefore a *lower bound* on run-to-run variance — it excludes initialisation variance (zero by construction here), augmentation-RNG variance (frozen) and hardware nondeterminism (not measured). Every threshold in this paper is calibrated on that lower bound, which makes the criteria *less* conservative than a full-variance calibration would be, not more. Sub-threshold cells are labelled as *not detected*, which is a power statement, not evidence of absence.

**Table T8.** The σ components behind the tier vocabulary, per cell (data-order seeds, n = 3; percentage points). The convention is §8.2's: σ is a (strategy × domain-pair) property, computed on the strategy side unless a row is labelled otherwise.

| cell (strategy × domain pair) | σ_b, baseline arm | σ_strategy, strategy arm |
|---|---|---|
| SHWD→SFCHD, lr0.005 | 0.18 | 0.13 |
| smoke→SFCHD, lr0.005 | 0.25 | 0.23 |
| MAFA→mendeley, sns | — | 0.26 |

The n = 3 sd estimation CI is **[0.5×, 6.3×]**. The two components the registered design excludes are reported separately in Appendix G: augmentation-RNG 0.246 pp (strategy arm) and 0.072 pp (baseline arm); initialisation 0.146 pp (gain SD) and 0.209 pp (absolute endpoint SD).



## F.2 The σ components in full (moved from §8.3, 2026-09-19)

*σ controls (the components the registered design excludes).* Three components are now separated by direct measurement on the same cell (SHWD→SFCHD, 100 epochs, 20% subset): data order (0.18–0.21 pp paired-difference), which is what the registered σ varies; augmentation RNG (strategy-arm **lr0.005** SD **0.246 pp**, baseline-arm SD **0.072 pp**, gains **+0.69 / +0.42 / +0.22 pp**, mean **+0.443 pp**, 3/3 positive); and initialisation (**SD 0.146 pp** across three from-scratch source endpoints, gains **+0.570 / +0.280 / +0.460 pp**, mean **+0.437 pp**, 3/3 positive), the absolute endpoint itself moving with SD **0.209 pp**. Initialisation is the **smallest** of the three, so it does not widen the σ bound, though on the corroborating cell the augmentation component does mean that it clears the registered threshold and **not** the augmentation-inflated one and is therefore carried by its conventional statistics; the full composition, with every sample size, is in **Appendix F.1**.

## F.3 The family-level reads (moved from §9.3, 2026-09-19)

**Family-level analysis.** The Benjamini–Hochberg correction [42] over the 26-configuration roster is reported as *robustness, not a family-wise guarantee*; its p-values, family sizes and the sensitivity table are in **Appendix F.1**. **The clean-protocol tier passes the same correction only after a seed extension, and we state both the pass and its provenance at the point of claim:** under the identical roster-wise convention its two cell tests at ten seeds become **q = 0.052** and **q = 0.127** — the stronger cell sitting above the line because 26×(2/2¹⁰) = 0.0508, an arithmetic property of the exact permutation floor [41] and not of the evidence — and at the eleven- and thirteen-seed extension **q = 0.0159** for both, clearing q = 0.05. That extension was undertaken with the ten-seed values known, so this correction cannot control the FDR of the family that generated the selection; the fresh-seed tests remain the BH-robust numbers.

# Appendix G. Key assumptions × plausible ranges (the fourth rule)

**The ε-scaling exponents behind §7.2(1), per cell (target-side worst direction, customary radii).** Fitting $S(\rho) \propto \rho^{k}$ on the two customary radii (0.001 → 0.003) of the released target-domain flatness readings gives: 0.66 (`sio_a_base_100ep`), 0.56 (`sio_a_jps_100ep`), 0.56 (`sio_a_jps_30ep`), 0.59 (`sio_a_pws_100ep`), 0.63 (`sio_css_30ep`), 0.58 (`sio_pws_30ep`), 0.81 (`sio_sns_30ep`) — median 0.59, all well below the ≈2 that a curvature-dominated read would require; the two pathological `spi` arms (which exist as a deliberate negative control) give 4.57 and 4.31, and at the third radius (0.01) the increments diverge by up to seven orders of magnitude, which is why the primary radius is fixed at 0.001. Source-side readings have only the 0.001 radius in the release, so no exponent is claimed for them.


**What was measured, and what was not (moved from §7.4).** **What was measured, and what was not.** The hierarchy above is a statement about the quantities *this study measured*: trajectory-evaluated first-order (gradient) reads and same-protocol relative diagnostics. A spectral read at the fine-tuned endpoints now exists as well (§4.2 and Appendix G: Lanczos with 20 iterations [31] over 220 endpoint pairs, Ritz residuals reported), but it is a *stochastic estimate at a computed checkpoint* — batch-draw dependent, reported as a distribution and used only as a diagnostic — and it is not a population spectrum. What it establishes is negative and about the assumption rather than the outcome: the *ball* form of H5 is refuted at every measured endpoint ($\lambda_{\min}<0$ in 220/220), so a curvature estimate from these artefacts would not supply the modulus the removed interaction term needed. Still unmeasured, and not measurable from these artefacts: $L$, $L'$, $W_1$, $r_T$ and the localization placement assumed in §4.2. Our claim is that *these* diagnostics are not outcome predictors, not that spectral quantities would fail as well. The stationary-side reads we do report (source-side spectral sharpness, §8.6) are computed by perturbation, not from a spectrum, and are deliberately not used as predictors.

| Assumption | Registered/plausible range | Sensitivity statement |
|---|---|---|
| L (loss Lipschitz const.) | order-dependent; not measured | enters C₁ only (additive), no grading impact |
| μ_T (target strong-convexity) | **measured at the checkpoints, and the ball form is refuted there**: $\lambda_{\min}(H_T)<0$ in **220 of 220** endpoint pairs; the ordered-pair form is what remains testable, and its secant modulus $\mu_{sec}$ is measured and changes sign across configurations (**75 negative / 145 positive**) | **the reading matters** — two-point strong convexity, not one-point growth; it scales the quadratic branch of Proposition 1 and $T_*$, and it is what makes a curvature term redundant under H5 while the weaker one-point reading does not (Appendix C step 5). Because the ball form fails at every measured endpoint, §4.2 states the quadratic branch under the **ordered-pair** form rather than under a ball |
| r_T (H5 radius) | not measured, and at the measured endpoints it is moot: a ball carrying H5's content requires $\lambda_{\min}$ to be bounded below by a positive $\mu_T$, and $\lambda_{\min}<0$ holds in 220 of 220 endpoint pairs, so no such ball exists there | H10 compatibility requires r_T ≥ √(4LW₁/μ_T); at observed D this is a mid-range requirement (corrected: an earlier draft had 4LW₁/μ_T² — the correction is recorded in Appendix E) |
| H10 small shift | D = 9.4–13.0 observed (W₁ proxy) | **a compatibility check only**: it relates the shift scale to the growth scale of H5, does *not* establish localization (Appendix C step 1), and is not a hypothesis of Corollary 1 or Proposition 1 |
| α′ (displacement exponent) | *withdrawn* — this row belonged to the generic-displacement estimate $2L'\sqrt{L/\mu_T}W_1^{3/2}$, which Appendix J.4 removes as never the lower envelope of the printed bound; treated here as a historical entry | the printed displacement bound uses the strong-convexity quadratic branch and Lemma 1's linear branch, and contains no α′ |
| ρ (perturbation radius) | 0.001 primary (protocol fact) | first-order dominated at target; three-tier decomposition provided |
| σ_b, σ_strategy | measured per Table T8 (n = 3) | headline-cell sensitivity table in §9.3 |
| augmentation-RNG component (the σ component the registered design excludes) | **measured**: strategy arm 0.246 pp, baseline arm 0.072 pp (n = 3 augmentation seeds, SHWD→SFCHD 100 ep) | σ is a lower bound by 1.07–1.89× of the data-order σ; below the 3× recalibration trigger for the 3σ line and the +0.4 pp module threshold (§8.2–§8.3, Appendix D) — so no recalibration is triggered, and the one cell whose margin was ≈1.1× the line is instead carried by its conventional statistics (Appendix F.1) |
| initialisation component (the other σ component the registered design excludes) | **measured**: gain SD 0.146 pp and absolute-endpoint SD 0.209 pp across 3 independent source trainings (3/3 positive gains, mean +0.437 pp; SHWD→SFCHD 100 ep) | the smallest of the three components: below the augmentation component (0.246 pp) and below the across-seed spread of the same clean-protocol cell (0.49 pp, §8.6), so it does not widen the σ bound; the endpoint movement (43.250–43.630%) is why every comparison here is a same-source-endpoint paired contrast |

**Which result uses which assumption.** Because the results no longer contain a curvature term and no
longer use a Taylor expansion, their assumption footprint is much smaller than earlier versions', and
the two branches of Proposition 1 have *different* footprints. We state the mapping rather than leave
it to be reconstructed.

| Assumption | Corollary 1 (gap) | Prop. 1, linear branch | Prop. 1, quadratic branch | Eq. (8) schematic (§6) | Lemma 8 (§5) | $\kappa^-_\Delta$ diagnostic (App. J.2) |
|---|---|---|---|---|---|---|
| H1 ($L$) | **yes** — Lemma 1 | **yes** — Lemma 1 twice | no | | | |
| H2 ($L'$) | no | no | **yes** — Lemma 2 | | | |
| H3 ($\beta$-smoothness) | no | no | no | | | |
| H4 ($M$) | no | no | no | | | yes — transferring curvature from $\xi$ to $\theta$ |
| H5 ($\mu_T,r_T$; **two-point**, and only for the ordered pair) | no | no | **yes** — the defining first-order inequality | | | |
| H6 (bounded parameter domain) | no | no | no | | | |
| H7 (isotropic curvature) | no | no | no | **yes** — the isotropic special case | | |
| H8 ($C^2$ regularity) | no | no | no | yes | | yes |
| H9 ($\mu_S$) | no | no | no | | **yes** — Lemma 8 | |
| H10 (small shift) | no | no | no — **a compatibility check, not a hypothesis** | | | |
| **localization** $\theta^*_S\in B(\theta^*_T,r_T)$ | no | no | **yes** (assumption) | | | |
| **source optimality** (used to drop the middle telescoping term) | no | **yes** | no | | | |
| **source stationarity** $\nabla R_S(\theta^*_S)=0$, or the directional VI | no | no | **yes** (assumption) | | | |
| **non-negative loss** $\ell\ge0$ | **yes** (assumption) | no | no | | | |

Four consequences worth stating. (i) **Corollary 1 needs H1 and $\ell\ge0$ only** — no strong
convexity, no localization, no stationarity, no displacement machinery, and (if the gap is defined via
an infimum) not even existence of $\theta^*_T$. (ii) **The two branches of Proposition 1 are not the
same result**: the linear branch $④\le2LW_1$ uses H1 and source-optimality alone, while the quadratic
branch uses H2, H5, localization and stationarity and does **not** use H1. Stating the proposition as a
whole therefore hides a stronger branchwise statement, and we state the footprints separately for that
reason. (iii) **H10 is not a hypothesis of any result here.** It relates the shift scale to the growth
scale of H5 and is retained as a compatibility check; it does not establish localization, and the
earlier claim that it did is withdrawn. (iv) **H6 is likewise not a logical assumption** of the
abstract statements above: a bounded domain is one way to make the Lipschitz constants uniform over
$\Theta$ (which the "for any $\theta\in\Theta$" quantifier wants) and one way to make the
sharpness family satisfy H1, but neither is a proof step, and we record it as such. H3 and H8 — a
global smoothness constant and $C^2$ regularity — are simply not needed by these results, since the
displacement bound uses the strong-convexity inequality rather than a Taylor expansion; they remain in
the assumption list because other remarks in the appendices invoke them.

**What the endpoint read suite measures, and what it leaves open.** Every row above marked "not
measured" was the section's largest remaining gap, and it is now partly closed. A read suite was run on
the released checkpoints; we state its protocol and its results together, because neither is meaningful
alone. **Protocol.** 220 endpoint pairs over **119 endpoints** — the 99 endpoints representing the
frozen roster (one baseline and one strategy arm per configuration, plus the full ten-seed arm of the
two outcome-significant cells) and the twenty endpoints of the `dota15→aitod` replication cell — each
read on 1, 2 or 4 batch draws of 4 batches × 4 images at 640 px, with the loss evaluated with the model
in training mode and every normalisation layer in evaluation mode, Lanczos with 20 iterations at the
target endpoint, and the source objective evaluated wherever the source and target classification heads
are compatible. Every quantity is an empirical value **at a computed checkpoint**, not at a population
minimiser. Released scripts: `theory_read_endpoint.py` (the read) and `analyze_reads.py` (the
aggregation); the ε-scaling and encoder-Jacobian tables of §7.2(1) are released alongside them as `theory_e2.csv` and `theory_e3.csv`. One provenance correction belongs with the protocol, because it changed numbers: an earlier version of the suite evaluated the loss in `eval()` mode, where the detection head runs NMS and the value is not the training risk. The correction changed the E2 table and left the forward-only E3 table byte-identical; the pre-correction tables are retained in the release under the `.evalmode_pre_r8` suffix rather than deleted.

| Quantity | Status | Measured over the 220 pairs |
|---|---|---|
| $\lambda_{\min}(H_T(\theta_T))$ | measured, **diagnostic only** | **negative in 220/220** |
| $\lambda_{\max}(H_T(\theta_T))$ | measured, **diagnostic only** | $5.2\times10^3$ to $1.1\times10^6$; not a modulus for $\|\Delta^{\top}H_T\Delta\|$ (**Appendix J.4**) |
| Ritz residuals of both extremes | measured (convergence check) | relative median $4.6\times10^{-4}$ and $6.1\times10^{-4}$; 90th percentile $2.7\times10^{-3}$ and $3.5\times10^{-3}$ |
| $\|\Delta\|$ | measured | median 4.5 (range 0.39–508) |
| $\widehat{④}=R_T(\theta_S)-R_T(\theta_T)$ | measured | **negative in 26/220** — so it is reported as a checkpoint loss difference, not as a non-negative cost |
| $\mu_{sec}$, the ordered-pair secant modulus | measured | **75 negative / 145 positive**, median 2.19 |
| source optimality $R_S(\theta_S)-R_S(\theta_T)$ | measured on the 164 head-compatible pairs | holds in **59/164** |
| source directional VI $\langle\nabla R_S(\theta_S),\Delta\rangle$ | same subset | holds in **32/164**; both hold together in **14/164** |
| $L$, $L'$, $W_1$, $r_T$, localization | **not measured, and not measurable from these artefacts** | Eqs. (4)–(5) remain scaling statements, as stated above |

Three consequences, stated rather than left to be inferred. (i) **The ball form of H5 is refuted at
every endpoint measured**: $\lambda_{\min}<0$ in 220 of 220 pairs, so no ball around a fine-tuned
endpoint carries H5's content. What remains testable is the **ordered-pair** inequality, and that is
what $\mu_{sec}$ measures — which is why §4.2 states the quadratic branch under that form rather than
under a ball. (ii) **Both source-side premises fail more often than they hold**, which is the empirical
reason the $\varepsilon$-forms of §4.2 and Appendix C steps 2–5 exist: they replace the two exact
conditions with measured residual terms, and are therefore not cosmetic. (iii) **A quarter of the pairs
cannot form the $\varepsilon$-certificate at all** (56/220), because the source checkpoint's
classification head has a different class count and is re-initialised, so $\nabla R_S$ is not a gradient
in the target's parameter space — the limitation §4.2 states. Two caveats on the whole table: the
Hessian quantities are batch-draw dependent (the relative spread of $\lambda_{\max}$ across draws of one
endpoint has median 0.52, of $\widehat{④}$ 0.26 and of $\mu_{sec}$ 0.36), so they are reported as
distributions over draws rather than as point values; and the sign of the source-side quantities is not
draw-stable in every case (it flips across draws of the same endpoint in 14 of 51 multi-draw endpoints
for source optimality and 11 of 51 for the directional VI), so those are reported as rates with that
instability disclosed rather than as per-cell verdicts.


## G.1 Assumption plausibility under detection losses (moved from §9.1)

**The full argument the main text now summarises.** The loss family's **data-Lipschitz constants** are finite and explicit: the box terms are $[0,1]$-valued and piecewise smooth in box coordinates that are themselves Lipschitz in the image through the regression head (needing the usual non-degeneracy of box denominators), and the classification term satisfies $L_{\rm cls}\le\mathrm{Lip}(u(\theta;\cdot))$, since $|\partial\,\mathrm{BCE}(\sigma(u))/\partial u|=|\sigma(u)-y|\le1$ and composition multiplies Lipschitz constants — so no logit clipping is required for H1 (the loss *value* is unbounded; its *sensitivity to the data* is not, which is what H1 needs). H6 enters here rather than in the derivation: it is what makes these constants **uniform over the parameter domain**, which the theorem's “for any $\theta\in\Theta$” quantifier requires; smoothness (H3) and Hessian-Lipschitz regularity (H4) hold for standard convolutional backbones away from non-differentiable points (the main text keeps this clause in compressed form); **H5 is not supported at the measured endpoints in its ball form** — $\lambda_{\min}(H_T)<0$ in 220 of 220 endpoint pairs, so no ball around a fine-tuned endpoint carries H5's content (the μ_T row of the assumptions×ranges table below) — and the bound's quadratic branch uses the **ordered-pair form** instead, whose secant modulus $\mu_{\rm sec}$ is measured and changes sign across configurations; and H10's compatibility at the observed shift range is an assumption-level statement, tabulated with its plausible ranges in this appendix.

## G.2 The ε-scaling reading in full (moved from §7.2, 2026-09-19)

(1) ε-scaling: at customary radii the target-domain worst-direction increment is first-order dominated — the read is $\rho\|\nabla R_T\|$, a slope/distance proxy, not curvature — and that is **measured**, not asserted: the two-point slope of the worst-direction increment against ρ at the two customary radii (0.001 → 0.003) gives exponents of **0.56–0.81 (median 0.59)** across the seven non-pathological target-side cells, far below the ≈2 a curvature-dominated read would require, while the third radius (0.01) diverges by up to seven orders of magnitude — which is why the protocol fixes the primary radius at 0.001; the two deliberately pathological `spi` arms are the exception at 4.3–4.6, as Appendix G records. The per-radius perturbation readings and the encoder-Jacobian spectral widths behind this reading are released as theory_e2.csv and theory_e3.csv in the read archive, recomputed after the evaluation-mode correction recorded in the protocol paragraph of Appendix G. (2) The cos-proxy flip chain (§6.2). (3) The SNR floor (18/18 < 2). (4) Gap-vs-flatness linear correlations vanish under the strict protocol. Contrast class: source-side stationary spectral reads hold at 253-284 (±6%) — 12 worst-direction readings at $\epsilon = 0.001$ on the source side, spanning 252.99–283.96, a relative spread of ±5.8% (released source-side flatness readings) — and source stationary positions are insensitive to the source-training loss (stage ablation, Appendix G). Unit note: source-side reads are worst-direction increments at a *relative* radius ρ‖θ‖ (‖θ‖ = 146.2 at the pretrained origin and 148–158 across the fine-tuned endpoints, Appendix M.1) expressed in *loss* units; radius and reading are in different units and must not be compared numerically, and ρ is given explicitly wherever a read is quoted.

# Appendix H. cos-proxy protocol details

Six protocols (v1 test-distribution; v3 train-distribution quasi-stationary; v3b frozen-reference variant of v3; v3c multi-checkpoint; v3d best-neighbour; v3e plateau + SNR gate) — §6.2 lists the five that enter the SNR table, and v3b appears only in the flip chain, 18 cells each (3 pairs × 2 budgets × 3 strategies), SNR = ‖d_π‖/‖g_ref‖ per cell, gate ≥ 2 — the gate asks the signal to exceed the residual reference by a factor large enough that sign, not merely magnitude, is resolvable. §6.2 reports the measured band and the cross-evaluator fluctuation against that gate. Full per-cell table and the flip chain (v3b vs v3c/d/e) in the released analysis archive.

---

## H.1 The cos-proxy protocol chain in full (moved from §6.2)

We tested the operationalisation with six protocols (Appendix H's preamble); the five that enter the SNR table form the progressively corrected chain below, and the sixth — v3b, the frozen-reference variant of v3 — appears only in the flip chain. The five: v1 (test-distribution gradients — invalidated: at a mismatched point $\mathbb{E}_{\text{test}}[\nabla\ell_0]\neq0$ and the difference gradient degenerates to $d_\pi \approx (s{-}1)g_{\mathrm{ref}}$, $s<1$); v3 (train-distribution quasi-stationary evaluation, where the stationary condition cancels the reference term); v3c (multi-checkpoint averaging); v3d (best-neighbour averaging); v3e (plateau averaging with an SNR gate). Outcome: across all 18 measurement cells (three domain pairs × two budgets × three strategies, every cell under the v3e plateau-averaged protocol with its SNR gate; the v3c/v3d variants each also produce 18 cells) the difference gradient is the same order as the residual reference gradient (**SNR ∈ 0.76–1.47, all below the prospectively frozen gate of 2**), and the sign of the alignment *ranking* flips with the evaluator variant (Spearman +1.00 under best-checkpoint averaging vs. −1.00 under neighbourhood averaging, over the three strategies per evaluation point; with n = 3 per point each extreme sign has permutation probability 1/6, so the flip is indicative — the decisive evidence is the SNR floor, which holds on all 18 cells and depends on no ordering). Mechanistically, at a *precise* stationary point $d_\pi$ is well-defined; finite-SGD training only reaches approximate stationarity, so the SNR stays O(1) in our runs — an empirical obstruction under finite-SGD, finite-batch training rather than an impossibility theorem (larger gradient batches, variance-reduced or fully-converged estimators are outside this protocol).


# Appendix I. The registered roster, enumerated cell-first (26 configurations, two pipelines)

**The registered family: what we can and cannot reconstruct (moved from §8.2).** **The registered family: what we can and cannot reconstruct.** The family was recorded as 28 strategy–pair cells constructed as "lr0.005 and the tested loss families × the seven domain pairs × budget tiers" (the released grading table, family entry), and 28 × 3 = 84 graded runs are reported. Re-deriving the roster from the released material yields **26 pair-able configurations, listed cell by cell in Appendix I (Table T10)**: 22 from the B pipeline and 4 from the SFCHD pipeline, whose runs postdate the registration snapshot and which carry **both** criterion-passing cells. The earlier version of this appendix enumerated only the first 26 and therefore excluded the two cells the paper is about; that inconsistency was found in the external audit pass and is corrected here rather than argued away. The recorded count of 28 is reported as the registration record and is used as a denominator nowhere; the two constructions we can check — seven pairs × four arm families (= 28) and the enumerated registry (= 26) — do not agree, and we cannot recover retrospectively which 28 cells the frozen count referred to, because the registration documents describe the family *by construction* rather than as an enumerated list. This is a defect in the registration record, and we state its consequences rather than absorb them: (i) in this paper "registered family" means the set of cells covered by the frozen criterion, not an independently auditable list; (ii) the family-level quantities — the expected number of null passes (0.37–1.65), the family-wise probability of at least one (31–82%), and the FDR family size — would inherit that uncertainty if they were computed on an undefined roster, so we do not leave them there: **every family-level quantity in this paper is computed on the 26-configuration enumerated roster of Appendix I**, and is labelled as such where it appears; the recorded count of 28 is reported as the registration record, not used as a denominator; (iii) a third party cannot reproduce the family-level arithmetic from the released files alone, which we flag as the paper's principal documentation gap. Two consequences are worth stating without hedging. First, at three seeds the family-level evidence is *consistent with the null* — two passes against 0.37–1.65 expected — so the screening tier is a selection device, not a result. Second, the claim therefore rests on the ten-seed replication, which we have already labelled as outcome-selected and which we report together with the seven-seed fresh subset that is not touched by the selection. A reader who accepts only the fresh subset still has both cells (p = 1.9×10⁻⁷ and 7.8×10⁻⁵); a reader who rejects the whole extension has no confirmatory evidence. Every graded number, by contrast, is a named run in the released tables, and every threshold is applied to a cell whose reading exists. Related accounting: the dual-metric analysis of §8.5 uses fifteen *long-budget* cells — the 100-epoch cells of five configurations of Table T10 under its three loss-prior strategy families, three cells per configuration: row 10 (fsin→firesmoke: css, sns, pws), row 11 (smoke→firesmoke: css, sns, pws), row 15 (mask→mask: css, sns, pws), row 20 (mafa→mende: css, sns, pws) and row 21 (mendein→mende: css, sns, pws). Each cell is contrasted with its own configuration's same-budget (`base100`) baseline on best-checkpoint mAP50 and mAP50-95, and the sign split is counted where mAP50 falls below zero and mAP50-95 does not; **four of the fifteen cells satisfy it**. This denominator is distinct from the 26-configuration roster, and the released runs behind every cell are named in Table T10.

Table T10 is the roster that every family-level quantity in this paper is computed on. Its enumeration rule is stated once and applied to both released sources: group the released runs by (**source pretraining endpoint → target corpus, budget**); a group containing a `base*` run (shapeiou @ lr0.001) **and** at least one strategy arm (`lr005`, `sns`, `css`, `pws`, `jps`) is one pair-able configuration; these five are the released **run-name** vocabulary, the three loss-prior families tested in this paper are `css`, `sns` and `pws`, and `jps` appears in one configuration’s recorded arms only. Arms are identified from the released **run-name convention** rather than from `args.yaml`, because the loss prior is injected at runtime (`losses.patch_loss`) and therefore never appears as a `loss:` field in the recorded arguments. Released script `enumerate_family_cellfirst.py` regenerates this table from the released run archive.

Two earlier versions of this appendix were wrong, and we record both errors rather than the correction alone. The first enumerated only the released *registration table* (135 runs, snapshot 2026-09-03), which contains **no SFCHD row**, and so omitted the two criterion-passing cells; the second attempted to repair that by appending four SFCHD groups but kept the mis-classification of loss-prior arms as baselines, which made several rows arithmetically unable to support the cells the paper reports (§6.3's `sns` at 3v3 against a single baseline run is the clearest example). Both defects were found in the external audit pass, not by our own checks, and the roster below is the corrected form.

**Table T10.** The registered roster, enumerated cell-first (26 configurations).

| # | pipeline | source → target | budget | baseline runs | strategy arms (runs[seeds]) | runs |
|---|---|---|---|---|---|---|
| 1 | within-domain | aitod_pretrain → aitod | 30 ep | 1 | lr005×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
| 2 | within-domain | dota_pretrain → dota | 30 ep | 1 | lr005×1[ns]; sns×1[ns] | 3 |
| 3 | within-domain | dota15_pretrain → dota15 | 30 ep | 1 | lr005×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
| 4 | cross-domain | visdrone_pretrain → dota15 | 100 ep | 10 | lr005×10[42,43,44,45,46,47,48,49,50,51] | 20 |
| 5 | within-domain | dota15_pretrain → dota15 | 100 ep | 1 | css×1[ns]; lr005×1[ns]; pws×1[ns]; sns×1[ns] | 5 |
| 6 | within-domain | fsin_pretrain → firesmoke | 30 ep | 1 | css×1[ns]; lr005×1[ns]; pws×1[ns]; sns×1[ns] | 5 |
| 7 | cross-domain | smoke_pretrain → firesmoke | 30 ep | 3 | css×1[ns]; lr005×3[43,44]; pws×1[ns]; sns×3[43,44] | 11 |
| 8 | within-domain | fsin_pretrain → firesmoke | 50 ep | 1 | lr005×1[ns] | 2 |
| 9 | cross-domain | smoke_pretrain → firesmoke | 50 ep | 1 | lr005×1[ns]; pws×1[ns]; sns×3[43,44] | 6 |
| 10 | within-domain | fsin_pretrain → firesmoke | 100 ep | 1 | css×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
| 11 | cross-domain | smoke_pretrain → firesmoke | 100 ep | 1 | css×1[ns]; lr005×2[ns]; pws×1[ns]; sns×3[43,44] | 8 |
| 12 | cross-domain | mafa_pretrain → mask | 30 ep | 1 | lr005×1[ns] | 2 |
| 13 | within-domain | mask_pretrain → mask | 30 ep | 3 | css×1[ns]; lr005×1[ns]; pws×1[ns]; sns×3[43,44] | 9 |
| 14 | within-domain | mask_pretrain → mask | 50 ep | 1 | lr005×1[ns] | 2 |
| 15 | within-domain | mask_pretrain → mask | 100 ep | 1 | css×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
| 16 | cross-domain | mafa_pretrain → mende | 30 ep | 1 | css×1[ns]; lr005×1[ns]; pws×1[ns]; sns×1[ns] | 5 |
| 17 | within-domain | mendein_pretrain → mende | 30 ep | 3 | css×1[ns]; lr005×1[ns]; pws×1[ns]; sns×1[ns] | 7 |
| 18 | cross-domain | mafa_pretrain → mende | 50 ep | 1 | lr005×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
| 19 | within-domain | mendein_pretrain → mende | 50 ep | 1 | lr005×1[ns] | 2 |
| 20 | cross-domain | mafa_pretrain → mende | 100 ep | 4 | css×4[43,44,45]; jps×2[44,45]; pws×1[ns]; sns×4[42,44,45] | 15 |
| 21 | within-domain | mendein_pretrain → mende | 100 ep | 2 | css×1[ns]; pws×5[42,43,44,45]; sns×1[ns] | 9 |
| 22 | SFCHD-pipeline | shwd2sf_pretrain → sfchd | 30 ep | 4 | lr005×4[42,43,44] | 8 |
| 23 | SFCHD-pipeline | shwd2sf_pretrain → sfchd | 50 ep | 3 | lr005×4[42,43,44] | 7 |
| 24 | SFCHD-pipeline | shwd2sf_pretrain → sfchd | 100 ep | 12 | lr005×13[42,43,44,45,46,47,48,49,50,51]; pws×1[ns]; sns×3[44,45] | 29 |
| 25 | SFCHD-pipeline | smoke_pretrain → sfchd | 100 ep | 11 | lr005×11[42,43,44,45,46,47,48,49,50,51] | 22 |
| 26 | within-domain | visdrone_pretrain → visdrone | 30 ep | 1 | lr005×1[ns]; pws×1[ns]; sns×1[ns] | 4 |
Which cells this roster covers, stated explicitly because that is what the previous versions failed at. The two criterion-passing cells are rows 24 (`SHWD→SFCHD`, 100 epochs, corroborating) and 25 (`smoke→SFCHD`, 100 epochs, strong), and rows 22–23 carry the corresponding shorter-budget arms that produce the budget curve of §8.3. The loss-prior and module cells of §6.3/§8.4 are rows 20 and 21 (`MAFA→mendeley`, `mendeley→mendeley`), whose `sns`/`css`/`pws` arms each carry three or more seeds, and row 24 also carries the `sns` arms used in §8.4's `SHWD→SFCHD` negative result. The `visdrone→dota15` directional probe is row 4 (ten seeds, both arms), and it is *not* counted as a family member in the multiplicity arithmetic below.

Four properties we state rather than leave to be discovered. (i) **The family size used for every multiplicity calculation is m = 26** — the number of pair-able configurations enumerated above — and it is the same 26 used in the BH corrections of §9.3 and in the family rows of Appendix F. The recorded registration count of **28** is reported as the registration record and is used as a denominator nowhere; it differs from 26 because it was written as a construction ("seven pairs × four arm families") rather than enumerated, a discrepancy we disclosed before this appendix existed and now make checkable. (ii) Of the 26, **twenty-two are B-pipeline and four are SFCHD-pipeline**; the SFCHD pipeline is where both passing cells live, a concentration (15% of the roster carrying 100% of the positive result) that we state here and in §8.2. (iii) The configurations are *configurations*, not arms: the "strategy arms" column lists three to five arm families per configuration, so the arm-level contrast count is larger than 26 — which is why family-level quantities are stated per configuration and the multiplicity family is named as this roster. (iv) Rows 4, 20 and 24 carry multi-seed arms (ten, three-plus and ten seeds respectively) because they host the pre-specified seed extension; the seed sets are printed per row, so a reader can see exactly which cells were extended rather than taking it from the text.## I.1 Run accounting from the released archive (moved from §8.1)

**Run accounting, stated from the released archive rather than from the registration record** (released `account_runs.py`). The archive contains **257 training runs with recorded arguments**: 11 source-pretraining runs (stage 1); **201 runs belonging to the 26 enumerated configurations** of Appendix I (both arms); 14 side-runs inside those configurations that the roster rule excludes (the 150/200-epoch side budgets and the source-transfer controls); and 31 runs from non-family blocks — 18 module/architecture-modification arms (the module block of §8.4 and its baseline), 5 un-prefixed MAFA→mask arms, 4 pipeline-repair runs, 3 three-epoch seed controls and one pretrain run whose recorded name predates the final convention. The registration record's own figures — 135 registered runs, 84 graded runs (28 cells × 3 seeds), 177 runs in total — describe that record at its 2026-09-03 snapshot; they **under-count the archive** because the SFCHD pipeline and the post-snapshot extensions are not in them, and they are reported as recorded and used as a denominator nowhere. Family-level arithmetic, the BH corrections and the roster all use the archive-based counts above; the pre-specified ten-seed extension (42 runs across three arms) is reported alongside the screening readings and is included in the 201.


**Table T12. The dual-metric accounting behind C4, cell by cell (recomputed from the released runs; same convention as Table T10: best-checkpoint endpoints, the same-budget `base100` baseline).** The fifteen cells are the 100-epoch strategy arms of the five configurations that carry the three loss-prior families.

| configuration | arm | runs | $\Delta$mAP50 (pp) | $\Delta$mAP50-95 (pp) | sign split |
|---|---|---|---|---|---|
| fsin | css | 1 | -0.14 | -0.07 | no |
| fsin | sns | 1 | -0.10 | +0.00 | yes |
| fsin | pws | 1 | -0.24 | -0.05 | no |
| smokefs | css | 1 | -0.17 | +0.08 | yes |
| smokefs | sns | 3 | +0.47 | +0.35 | no |
| smokefs | pws | 1 | +0.78 | +0.44 | no |
| mask | css | 1 | +0.01 | +0.01 | no |
| mask | sns | 1 | +0.00 | +0.05 | no |
| mask | pws | 1 | -0.01 | -0.00 | no |
| mende | css | 4 | -0.28 | +0.27 | yes |
| mende | sns | 4 | -0.33 | -0.20 | no |
| mende | pws | 1 | -0.28 | +0.15 | yes |
| mendein | css | 1 | -0.41 | -0.60 | no |
| mendein | sns | 1 | -0.42 | -0.56 | no |
| mendein | pws | 5 | +1.03 | +0.17 | no |

Marginals over the fifteen cells, printed as a **range** because one of the fifteen $\Delta$mAP50-95 differences is exactly zero and its sign convention moves the count: **10 of 15** have $\Delta$mAP50 $<0$ and **9–10 of 15** have $\Delta$mAP50-95 $\geq 0$ (10 if the exact zero is counted as non-negative, 9 if it is not); the number of cells showing both signs is **5**, and under independence the expectation would be **5.3 to 6.7**, so the observed count does not exceed chance under either convention.

*Reading.* The two metrics move in opposite directions in four cells (rows marked yes) — that is the count the main text reports. The marginals are printed beside it as a **range, not a point**, for two reasons, and both are stated so that the count can be re-derived: (i) one of the fifteen $\Delta$mAP50-95 differences is $-0.00$, so counting it as negative gives **9** of 15 non-negative in mAP50-95 and counting it non-negative gives **11**; (ii) the $\Delta$mAP50 marginal is **9** of 15 on the released runs, and the point value **10** appears only under a different aggregation of the cells carrying more than one run. Across that range independent signs would already give **5.4–7.3** such cells, so the observed four is a **description of this accounting, not evidence of a mechanism or of a family-level law**; the cell-level mechanism evidence is the per-class decomposition the main text points to, which is measured on **two** cells — the minority-class recall cost on SHWD→SFCHD and the coverage channel on the dota15 probe — and is reported as such, cell by cell. Seed counts are in the `runs` column: 11 of the 15 cells are single-run, four carry paired seeds, and the table is therefore a sign accounting rather than a test.

# Appendix J. The joint bound of §4, its derivation and its empirical reading

This appendix carries the material that the main text states only as motivation: the gap corollaries and their elementary character, the sharp optimal-displacement proposition, the correction that **removed** the interaction term we previously claimed, the assumption conditions the earlier derivation used without naming, and the diagnostic that replaces the curvature term — including the pre-specified prospective test that partially failed. §4 records what the reader needs in order to know what kind of statement the bound is; this appendix records everything that would be checked if the bound were the contribution, which it is not. **J.0 carries the term-by-term accounting moved out of §4.5 on 2026-09-26** (page budget; see the migration note in that section).

## J.0 The term-by-term correspondence moved from §4.5 (2026-09-26)

**The shift term.** Unbounded here, and the only term with an *independent* measurement attached: the shift distance on which every cell is ordered (§8.2) proxies the transport discrepancy underlying it. Neither bounds the other; both name the same axis, which is why §5.2's ordering is stated and then demoted to a three-point heuristic (§9.4).

**The source-side residual — the only term the experiment tests directly.** This is the optimisation error at the reported checkpoint, and it is the term a strategy acts on: §5.1 resolves it over the budget as $a_\pi\,h(T)$, so the model's prediction about the convergence axis is a prediction about this term, not about the gap. That yields the one quantitative, time-resolved claim this theory contributes: **under strategy $\pi$ the residual follows $a_\pi h(T)$**, positive and decreasing below the threshold $T_*$ of §5.1 and negative above it. The graded cells are consistent with it in the direction it predicts, the architecture-level repeat locates the crossover for that family at a budget where the baseline has already converged, and the third cell carries it to a target the registered family does not contain (§8.3). This is a correspondence to a *pattern of readings*, not a fit: the constants of $h$ are not estimated, and no reading here is a measurement of that term alone.

**The source-optimal approximation term.** Nothing here measures it and no claim rests on it; the experiment supplies only *negative* results about interventions that would move it — the three box-regression loss priors and the structure modules, reported as no detectable steady-state gain (§8.4). Reading those as evidence about this term would require a prior's benefit to land there and nowhere else; §4.3(i) is the general reason we do not assume it.

**The optimal-displacement cost.** This is the term §4.2's sharp bound prices, in two branches with different assumption footprints. It is **not measured** here: that would need $L$, $L'$, $W_1$ and the modulus, of which only the modulus is measured, and the conditions for the quadratic branch fail at the computed checkpoints. It is offered as sharpness about an inequality, not as a quantity to be checked.

**One assumption fails at the measured endpoints, and the bound survives it.** The ordered-pair form of H5 is what the sensitivity bound of §4.2 consumes, and it does not hold where the measurements are taken: $\lambda_{\min}(H_T)<0$ in **220 of 220** endpoint pairs, so no ball carrying that content exists at any checkpoint we can read (Appendix G). The relevant distinction is between a **definitional** hypothesis, which states what the setting is (the finite Lipschitz constant of the loss) and is met by construction, and an **admissibility** condition, which states where a statement is licensed (the ball form and the two conditions behind the quadratic branch) and can simply fail at the points we compute. What follows is about licence, not truth: the quadratic branch is unavailable at these endpoints, the bound is not falsified by that, and the linear branch is unaffected — it needs the Lipschitz constant and a common parameter space and nothing else. Where the two domains' class counts differ the head is re-initialised and neither branch exists, which is the one case these artefacts cannot repair.

**The direction of the coupling.** One term of four is tested, as a *response to a strategy* rather than a magnitude; the other three are named, bounded or deliberately left alone, and none is confirmed by any reading here. An empirical regularity can support the claim that the source-side residual responds to the optimisation path; it cannot confirm the other terms, however many cells agree. It also locates where a future experiment would aim — the displacement cost, the one term with a sharp bound and no measurement.

## J.1 The two statements and their scope

> **Assumptions at a glance (H1–H10)**. H1 loss Lipschitz in data ($L$); H2 gradient Lipschitz in data ($L'$); H3 β-smoothness (retained for the anisotropic remark; **not used by the results of §4**); H4 Hessian operator Lipschitz ($M$; retained for the anisotropic remark and the diagnostic, **not used**); H5 target-side local strong convexity ($\mu_T$, radius $r_T$; read as the **two-point** inequality, which is what Proposition 1 uses — Corollary 1 does not use H5 at all — and the weaker one-point growth reading does not suffice); H6 bounded parameter domain; H7 isotropic curvature approximation; H8 C² regularity (**not used by the results of §4**); H9 source-side local strong convexity ($\mu_S$); H10 small shift $W_1 \le \mu_T r_T^2/4L$ (**a compatibility check only** — it does not by itself place $\theta^*_S$ in the strong-convexity ball). Three conditions that the earlier derivation used without naming are stated here and carried as explicit hypotheses: **localization** $\theta^*_S\in B(\theta^*_T,r_T)$, **source stationarity or the directional variational inequality** ($\nabla R_S(\theta^*_S)=0$ for an interior minimiser, or $\langle\nabla R_S(\theta^*_S),\Delta\rangle\le0$, which holds when $\Theta$ is convex and is otherwise assumed), and **non-negative loss** $\ell\ge0$. Neither Corollary 1 nor Proposition 1 contains **any curvature term**; the $\lambda_{\max}$ convention belongs to the diagnostic of this appendix, and the measurement protocol's relative radius $\epsilon = \rho\|\theta\|\hat v$ is the convention used in §7. Localization is assumed directly and H10 is only a compatibility check between the shift scale and the growth scale of H5; it should not be read as supplying the placement, and the earlier claim that $\theta^*_S$ lies in the ball *because* of H10 is withdrawn.

**The two statements, restated for reference.** Under H1 and $\ell\ge0$, for **any** parameter value $\theta\in\Theta$:

$$\mathrm{Gap}_T(\theta) \;\le\; {R}_S(\theta) + L W_1 \qquad (\ell\ge0) \tag{4}$$ (Corollary 1), and, under H1, H2, H5 in its two-point form **with localization**, and source stationarity, $$④ \;\le\; \min\Bigl\{2LW_1,\; \frac{L'^2}{2\mu_T}W_1^2\Bigr\}. \tag{5}$$ (Proposition 1). Neither statement assumes all of H1–H10; the usage matrix of Appendix G gives the exact footprint of each, and the branch-specific footprints differ (the linear branch needs H1 and source-optimality; the quadratic branch needs H2, H5, localization and stationarity, and not H1).

The first inequality is the **elementary** target-gap corollary — Lemma 1 plus non-negativity — and it contains no displacement term; we label it elementary because that is what it is. The second is the **sharp optimal-displacement sensitivity** of Proposition 1, and it does **not** improve the first: since $R_T(\theta^*_T)\ge0$, the displacement term is redundant for the gap bound, and we say so rather than let a sharp component estimate be read as a sharp overall bound. What the displacement analysis contributes is the magnitude of $④$ and the sharpness of its constant — $1/(2\mu_T)$, attained exactly by the point-mass family of Appendix C step 4 — not a tightening of Eq. (4). The two branches of Eq. (5) cross at $W_1=4L\mu_T/L'^2$ (quadratic below, linear above), and the $W_1^{3/2}$ estimate that earlier versions printed is never the lower envelope of the two, so it is not used as a bound anywhere; it is printed only in **Appendix C**, at the point where the retraction is explained, and is marked withdrawn there. **No spectral quantity, no transfer constant and no $\mathcal{O}(\cdot)$ remainder appears**, and H3, H4, H8, Lemma 4 and the curvature-transfer lemma are all unused. The source-domain optimisation residual $\varepsilon_{\mathrm{opt}}(\theta) := R_S(\theta) - R_S(\theta^*_S)$ is term ② of the decomposition (Eq. 3), *contained in* $R_S(\theta)$, whose budget dependence is the convergence axis modelled in §5. Both statements hold for *any* θ — including the source-training endpoint $\theta_{\mathrm{src}}$ and the fine-tuned endpoints $\theta_{\pi,T}$ that the experiments grade (the model–experiment correspondence is parameterised in §7.4) — and both are in population risks and deterministic; the empirical layer is deferred to the omissions note below. **What kind of statement this is.** Neither is a numerically tight bound. The gap corollary is elementary and we say so; the displacement proposition is a sharp statement about a quantity the gap bound does not need. Telescoping Eq. (3) one step further gives the exact identity $\mathrm{Gap}_T(\theta) = [R_T(\theta)-R_T(\theta^*_S)] + \text{④}$, and Lemma 1 gives $R_T(\theta)\le R_S(\theta)+LW_1$; since $R_T(\theta^*_S)\ge0$, the gap corollary follows directly, with no displacement term. Printing $R_S(\theta)$ and $\varepsilon_{\mathrm{opt}}$ side by side charges the source risk twice, and an earlier draft of this section did exactly that; the statement above is the corrected form. When the optimisation residual is the quantity of interest, the two-KR variant is the form to quote — $\mathrm{Gap}_T(\theta)\le\varepsilon_{\mathrm{opt}}+2LW_1$, which is also displacement-free — and it must not be combined with the $R_S(\theta)$ form. No graded claim rests on overall numerical tightness.

**Deliberate omissions, and three conditions that used to be omitted assumptions rather than terms.** The authors record both kinds, because the distinction matters. *(Omitted terms.)* First, a source-complexity term $C_2S_S(\theta)$ is derivable by a PAC-Bayes argument but has no testable content here, so it is a remark (that theory supplement, Remark 6), not a theorem term. Second, the theorem contains **no curvature term at all**. The one the decomposition invites is removed for the two independent reasons set out below; where a curvature term is genuinely required (negative directional curvature), the correct modulus is $\kappa^-_\Delta$, kept out of the theorem because it would need the displacement-stability assumption that H5 currently supplies and because it is measured on computed endpoints rather than population ones. The perturbation-measured flatness is likewise a measurement remark — it matches curvature only at stationary points and is first-order dominated elsewhere — whose limits are the subject of §7. Third, the statements are deterministic and in population risks; the empirical version carries the standard uniform-convergence surcharge, which we keep outside because its constants are never calibrated here (§9.3) and no graded claim rests on it. *(Conditions that were assumptions in disguise.)* Three conditions the earlier derivation used without naming are stated in the box above and carried as explicit hypotheses: **localization** ($\theta^*_S$ lies in the strong-convexity ball — this is the one H10 does *not* supply), **source stationarity or the directional variational inequality**, and **non-negativity of the loss**. The assumption-usage matrix of Appendix G is built against this list, and H10 appears there as a compatibility check rather than as a hypothesis.



## J.2 Empirical reading: bounded, and not a validated predictor

The strict-protocol regression of the target-gap proxy on flatness gives $r = +0.004$ ($n = 22$ endpoint readings — source-stationary and fine-tuned endpoints across budgets and strategies, as tabulated in the released flatness files; $p = 0.99$) across budgets — no linear relationship — so the flatness proxy does not act as an empirically calibrated predictor of the target gap within the normal range. This regression was the test we designed for the interaction term of earlier versions; with that term now **removed** from the theorem (Appendix C step 5), it stands as a diagnostic result — the endpoint geometry carries no predictive signal on these cells, which is consistent with the correction and is one reason we do not put a curvature term in the theorem.

**Erratum (2026-09-11).** Earlier versions *regime-ised* this term on a single pathological configuration described as "target-side flatness ≈ 33× the normal range, collapsing across budgets (−2.4 pp at 30 ep, −2.0 pp at 100 ep)". Neither element reproduces. (i) *The 33× figure has no traceable measurement*: under the canonical protocol (worst-direction increment at the relative radius $\rho\|\theta\|$, shapeiou reference loss, test split) the ratio between that run and its matched family baseline is **1.6× / 2.0× / 3.4×** at ρ = 0.001 / 0.003 / 0.01, and the legacy readings behind the published number exceed the canonical ones by three to six orders of magnitude at ρ ≥ 0.003, the gap growing with radius — the signature of a perturbation that was not normalised to the relative radius. (ii) *The collapse does not reproduce*: over matched same-seed baselines the reweighted-prior variant gains +0.15 pp at 30 epochs (−0.06 / +0.35) and +0.01 pp at 100 epochs (−0.14 / +0.24 / −0.06). (iii) The cell was also mis-attributed: `mendein-pws` is mendeley→mendeley, not MAFA→mendeley. The erratum is recorded in the audit trail (Appendix E) and in the released grading table.

**A pre-specified prospective test that partially failed.** Before any outcome data for the new pairs existed we specified that the source-endpoint far-field read (worst-direction increment at ρ = 0.01, measured *before* fine-tuning) should sort the sign of the lr0.005 gain, and tested it on two further pairs. On those two **prospective** cells the record is 1/2: it held on visdrone (lowest read of the new pairs, 283 → measured −0.28 pp) and **failed on mask — the largest read of the seven (59,248) — where the measured gain is −2.69 pp** (−2.64 pp at 30 epochs as well). The three pairs that motivated the rule (SHWD→SFCHD 7,334 → +1.76 pp at ten seeds; MAFA→mendeley 2,534 → −1.40 pp at three seeds (per-seed −1.13 / −1.82 / −1.26) and mendeley→mendeley 323 → −0.7 pp, a single-seed 100-epoch reading, each against its own baseline — the latter replacing a −2.27 pp figure printed in an earlier version that we cannot trace to any released run) are its derivation set and cannot count as evidence for it; we report them only so that the bookkeeping conventions in the released material reconcile — counting them in gives 4/5 across all five cells, and 3/4 restricted to same-pipeline cells (the cross-pipeline reference SHWD→SFCHD excluded), which is the count carried in the grading table. Neither convention is a prospective pass. The read is therefore reported as an *exploratory observation, not a validated predictor*; note further that the failing domain's loss scale differs by an order of magnitude (L ≈ 1,795 versus 137–283 elsewhere), so the read's cross-domain comparability is itself unestablished.

We accordingly do **not** retain the interaction term. It is removed from the theorem as redundant under H5 and mis-modulused where a curvature term is needed, and its directed replacement $\kappa^-_\Delta$ is reported as a diagnostic. What remains open is not whether the curvature object predicts the gap — on our measurements it does not — but whether a scale-free geometry measure or a deliberate curvature-induction experiment could give it content. The additive terms ($R_S(\theta)$, which contains $\varepsilon_{\mathrm{opt}}$, and $C_1W_1$) continue to be exercised through the budget–strategy analysis of §5 and §8.3; the withdrawn $C_4W_1^{3/2}$ branch is **not** exercised and is printed only in the retraction above.

## J.3 Proof-level detail moved from §4 (the derivation the main text now states)

Kept here so that shortening §4 removed no content. **The quadratic branch needs no Taylor expansion.**
Applying the *defining first-order inequality* of $\mu_T$-strong convexity at $\theta^*_S$ with
$y=\theta^*_T$, rearranging and completing the square,

$$④\;\le\;a-\tfrac{\mu_T}{2}\|\Delta\|^2\;\le\;L'W_1\|\Delta\|-\tfrac{\mu_T}{2}\|\Delta\|^2\;\le\;\frac{L'^2}{2\mu_T}W_1^2,\qquad a:=\langle\nabla R_T(\theta^*_S),\Delta\rangle,$$

where the first step is the strong-convexity inequality, the second is $a\le L'W_1\|\Delta\|$ (the
inner-product estimate of Appendix C, valid in both the interior and the constrained case), and the
third maximises $L'W_1d-\tfrac{\mu_T}{2}d^2$ over $d\ge0$. **No bound on
$\|\nabla R_T(\theta^*_S)\|$ is used anywhere** — that quantity is controlled only in the interior case,
where it equals $\|\nabla R_T-\nabla R_S\|$, so a norm-based chain would silently exclude constrained
minimisers. **No Taylor identity, no $C^2$ regularity and no $\beta$-smoothness is used** —
differentiability is part of H2's formulation, not a consequence of it — so H3, H8 and Lemma 4 are
unnecessary for this result. The linear branch is the two-KR telescoping of §4.1 with the middle term
dropped by source-optimality. **Sharpness** is exhibited by the point-mass family of Appendix C step 4,
which attains Eq. (5)'s quadratic branch exactly; there $w$ is taken small enough that both minimisers
lie in $\Theta$, that localization holds, and that the quadratic branch is the active one.

**What Corollary 1 presupposes about well-definedness.** Only that the objects are well defined: finite
first moments for $W_1$, measurability and integrability of $\ell(\theta,\cdot)$, finite risks
(Lemma 1), and a target minimiser — or an infimum if attainment is not assumed, in which case the same
proof gives the slightly more general form with $\inf_\vartheta R_T(\vartheta)$.

**Why this section is shorter than it was.** An earlier version argued its own scope three times over
(here, in §4 and in the appendix's opening paragraph). The scope statement is now made once, at the
point of claim (§4), and this appendix carries the derivation. The analytical-motivation paragraph of
that version is deleted rather than moved: its content is the scope statement plus a pointer to §5–§8,
both of which are above.

## J.4 The curvature-term retraction (what §4.3 of earlier versions stated)


**The curvature term that is not available, and what replaces it.** Earlier versions printed a $W_1\times$ top-curvature term. It is not available, for two independent
reasons (algebra in Appendix C step 5): with H5 read as genuine two-point strong convexity the quadratic
term of the second-order identity is non-negative, so the displacement cost is bounded by its first-order
part alone and $C_3W_1\lambda_{\max}(H_T(\theta))$ adds only slack; and if strong convexity is weakened
to one-point growth the modulus is wrong — $|x^\top H_Tx|\le\max(\lambda_{\max},-\lambda_{\min})\|x\|^2$,
and the case that needs the term is exactly the one where a *negative* eigenvalue exceeds $\lambda_{\max}$
in magnitude. What a non-strongly-convex analysis needs is the negative part of the **path** quantity:
the negative directional curvature
$\kappa^-_\Delta(H_T)=\max\{0,-\widehat\Delta^\top H_T\widehat\Delta\}$ taken over the displacement
segment, because over the 220 endpoint pairs the directional curvature **changes sign along the displacement in 168 of them (76%)** and its endpoint
value disagrees in sign with the ordered-pair secant modulus in 87, so a value at either end is not the object. It stays out of the bound and is reported as a same-protocol relative diagnostic (§7.4), which is the use that section permits (results in Appendix J.2). For the same reason the generic-displacement estimate
$2L'\sqrt{L/\mu_T}\,W_1^{3/2}$ is **withdrawn**: it is never the lower envelope of Eq. (5)'s branches, so
it cannot be the active one and cannot be asymptotically sharp under strong convexity.

**Assumption footprints, in one line.** Corollary 1 needs H1 and $\ell\ge0$ only; Proposition 1's
**linear** branch needs H1 and source-optimality, while its **quadratic** branch needs H2, the two-point
strong-convexity inequality for the ordered pair, localization and source stationarity and does **not**
use H1. **Which result uses which assumption** is tabulated in Appendix G, the H1–H10 box is in
Appendix J.1, and localization is assumed directly — the earlier claim that $\theta^*_S$ lies in the
strong-convexity ball *because* of H10 is withdrawn.

Term ④ is the optimal-displacement cost $R_T(\theta^*_S)-R_T(\theta^*_T)$; write $\Delta := \theta^*_S-\theta^*_T$.

1. **The two conditions the argument needs, named.** (a) *Localization*: $\theta^*_S$ lies in the ball $B(\theta^*_T,r_T)$ on which H5 holds — an assumption. H10 does **not** supply it: H10 bounds $W_1$ relative to the growth scale, but a source minimiser sitting in a distant well that is only $O(LW_1)$ worse than the target well is not excluded by it, and deriving the displacement bound from local growth at $\theta^*_S$ would presuppose the very placement being established. A readable sufficient condition is the basin-separation certificate $\inf_{\theta\in\Theta\setminus B(\theta^*_T,r_T)}[R_T(\theta)-R_T(\theta^*_T)]>2LW_1$, together with $\sup_\Theta|R_S-R_T|\le LW_1$: then $R_S(\theta)>R_S(\theta^*_T)$ for every $\theta$ outside the ball, so no global source minimiser lies there. We state localization as an assumption and give the certificate as a check. (b) *Source stationarity, or the directional variational inequality*: $\nabla R_S(\theta^*_S)=0$ for an interior minimiser; the weaker condition $\langle\nabla R_S(\theta^*_S),\Delta\rangle\le0$ suffices and is what the argument uses. That inequality follows from first-order constrained optimality **when $\Theta$ is convex** and $\theta^*_T\in\Theta$; if convexity is not assumed it is an explicit assumption. Boundedness of $\Theta$ is neither sufficient nor the relevant condition, and an earlier version's appeal to it ("$\Theta$ bounded and $\theta^*_T$ reachable") is withdrawn. 2. **First-order term (Lemma 2, source stationarity) — inner-product form, which covers both cases.** Write $a=\langle\nabla R_T(\theta^*_S),\Delta\rangle$ and split it as $\langle\nabla R_T(\theta^*_S)-\nabla R_S(\theta^*_S),\Delta\rangle+\langle\nabla R_S(\theta^*_S),\Delta\rangle$. The first term is $\le L'W_1\|\Delta\|$ by Lemma 2 and Cauchy–Schwarz; the second is $0$ when $\theta^*_S$ is an interior minimiser ($\nabla R_S(\theta^*_S)=0$) and $\le0$ when it is a constrained minimiser satisfying the directional inequality $\langle\nabla R_S(\theta^*_S),\Delta\rangle\le0$ — which follows from constrained optimality when $\Theta$ is convex and $\theta^*_T$ is feasible, and is otherwise an explicit assumption. Hence $a\le L'W_1\|\Delta\|$ in **both** cases. **The $\varepsilon$-form, which is what released checkpoints can support.** A reproduced endpoint is not a minimiser: $\nabla R_S(\widehat\theta_S)\ne0$ at a checkpoint, and no measurement can confirm an exact stationarity or an exact variational inequality. Write $\varepsilon_{\mathrm{st}}:=\|\nabla R_S(\theta^*_S)\|$. The same inner-product split then needs neither case analysis nor exactness, because the second inner product is bounded by Cauchy–Schwarz in *every* case: $$a=\langle\nabla R_T-\nabla R_S,\Delta\rangle+\langle\nabla R_S,\Delta\rangle\;\le\;L'W_1\|\Delta\|+\varepsilon_{\mathrm{st}}\|\Delta\|=(L'W_1+\varepsilon_{\mathrm{st}})\|\Delta\|.$$ $\varepsilon_{\mathrm{st}}$ is measured directly at the computed source endpoint on head-compatible pairs (the read suite reports $\|\nabla R_S\|$ there), so the **source first-order contribution** becomes measurable rather than assumed; localization, strong convexity and the constants of Lemma 2 remain hypotheses, so this is not a discharge of the proposition. $\varepsilon_{\mathrm{st}}=0$ is **sufficient but not necessary** for the exact case, and the exact case is therefore *not* the $\varepsilon_{\mathrm{st}}=0$ special case: on $\Theta=[0,1]$ with $R_S(\theta)=\theta$, the constrained minimiser $\theta^*_S=0$ has $\|\nabla R_S(0)\|=1$ and yet $\langle\nabla R_S(0),\theta^*_S-\theta^*_T\rangle=-\theta^*_T\le0$, so the directional inequality holds exactly with $\varepsilon_{\mathrm{st}}=1$. Two consequences we state rather than leave implicit: the residual-norm form can be substantially **looser** than the directional term it replaces — the exact gap is $\varepsilon_{\mathrm{st}}\|\Delta\|(1-\cos\phi)$, which can be as large as $2\varepsilon_{\mathrm{st}}\|\Delta\|$ — and the measured ratio $\varepsilon_{\mathrm{st}}/(L'W_1)$ is what says how much the stationarity assumption was worth, not whether it held. (An earlier version of this step added the variational term to a *norm* estimate, $\|\nabla R_T(\theta^*_S)\|\le L'W_1+\cdot$; that is not a valid inference — a scalar cannot be added to a norm bound — and it is replaced by the inner-product argument above, which also removes the need to assume an interior minimiser.) 3. **Sharp quadratic sensitivity — no Taylor expansion.** Applying the *defining first-order inequality* of $\mu_T$-strong convexity at $\theta^*_S$ with $y=\theta^*_T$, $R_T(\theta^*_T)\ge R_T(\theta^*_S)+\langle\nabla R_T(\theta^*_S),\theta^*_T-\theta^*_S\rangle+\tfrac{\mu_T}{2}\|\Delta\|^2$, and rearranging, $$④\;\le\;a-\tfrac{\mu_T}{2}\|\Delta\|^2\;\le\;L'W_1\|\Delta\|-\tfrac{\mu_T}{2}\|\Delta\|^2\;\le\;\frac{L'^2}{2\mu_T}W_1^2,$$ where $a:=\langle\nabla R_T(\theta^*_S),\Delta\rangle$; the second step is step 2's inner-product estimate $a\le L'W_1\|\Delta\|$, and the third completes the square (the maximum of $L'W_1d-\tfrac{\mu_T}{2}d^2$ over $d\ge0$ is $(L'W_1)^2/(2\mu_T)$, attained at $d=L'W_1/\mu_T$). With step 2's $\varepsilon$-form in place of exact stationarity, the same completing of the square gives $$\text{④}\;\le\;\frac{(L'W_1+\varepsilon_{\mathrm{st}})^2}{2\mu_T},$$ which returns Eq. (5)'s quadratic branch at $\varepsilon_{\mathrm{st}}=0$ and is close to it when the residual is small against $L'W_1$. This $\varepsilon$-form relaxes the stationarity condition only; the strong-convexity inequality it is built on is still applied to the ordered pair, so localization remains an assumption here exactly as it is above. If localization additionally supplies $\|\Delta\|\le r_T$, maximising over all $d\ge0$ is loose: the maximum over $0\le d\le r_T$ is $(L'W_1+\varepsilon_{\mathrm{st}})^2/(2\mu_T)$ when $r_T\ge(L'W_1+\varepsilon_{\mathrm{st}})/\mu_T$, and $(L'W_1+\varepsilon_{\mathrm{st}})r_T-\tfrac{\mu_T}{2}r_T^2$ otherwise. **No bound on $\|\nabla R_T(\theta^*_S)\|$ is used anywhere in this chain**: that norm is controlled only in the interior case, where it equals $\|\nabla R_T(\theta^*_S)-\nabla R_S(\theta^*_S)\|$; for a constrained minimiser it is not small, so a norm-based chain would silently exclude constrained minimisers. **No Taylor identity, no $C^2$ regularity and no $\beta$-smoothness is used** — differentiability is part of H2's formulation, not a consequence of it — so H3 and H8 are unnecessary for this result, and Lemma 4's identity is not needed at all. Note also that the quadratic branch needs the strong-convexity first-order inequality only for the *ordered pair* $(\theta^*_S,\theta^*_T)$, not on a whole ball; the ball version is kept because it is the natural and checkable statement. 4. **Sharpness of the $1/(2\mu_T)$ constant.** Two point masses at $z=0$ and $z=w$ (so $W_1=w$) with $\ell(\theta,z)=\tfrac\mu2\theta^2-cz\theta+B$ on bounded parameter and data domains give $R_S(\theta)=\tfrac\mu2\theta^2+B$ and $R_T(\theta)=\tfrac\mu2\theta^2-cw\theta+B$, so $\theta^*_S=0$, $\theta^*_T=cw/\mu$, $L'=c$ and $④=R_T(0)-R_T(cw/\mu)=c^2w^2/(2\mu)=L'^2W_1^2/(2\mu_T)$ — **equality**, so the quadratic bound is attained exactly and its constant cannot be improved. (The family satisfies the data-Lipschitz, smoothness and strong-convexity requirements on bounded domains; $w$ is taken small enough that both minimisers lie in $\Theta$, that localization holds, and that the quadratic branch is the active one of the minimum.) 5. **Linear fallback, and why the $W_1^{3/2}$ estimate is retired.** From the telescoping identity of Eq. (3), $④=[R_T(\theta^*_S)-R_S(\theta^*_S)]+[R_S(\theta^*_S)-R_S(\theta^*_T)]+[R_S(\theta^*_T)-R_T(\theta^*_T)]$, whose middle term is $\le0$ by source-optimality, so Lemma 1 applied to each bracket gives $④\le LW_1+LW_1=2LW_1$; this route uses no smoothness and no strong convexity. **Carrying that middle term instead of dropping it removes the assumption altogether:** $$④\;\le\;2LW_1+\bigl[R_S(\theta^*_S)-R_S(\theta^*_T)\bigr],$$ and the bracket is an evaluated quantity rather than an assumption — it is reported at the computed endpoints. This is the only branch needing nothing beyond H1, which is why it is the branch that a released-checkpoint measurement can bear on; §4.2 mirrors both $\varepsilon$-forms so that the main text and this appendix state the same objects. The three available branches cross pairwise at $W_1=L\mu_T/L'^2$ (linear vs $3/2$), $4L\mu_T/L'^2$ (linear vs quadratic) and $16L\mu_T/L'^2$ ($3/2$ vs quadratic). Hence the $3/2$ branch is **never the smallest**, and it cannot be asymptotically sharp under genuine strong convexity: $④/W_1^{3/2}\le(L'^2/2\mu_T)\sqrt{W_1}\to0$ as $W_1\to0$. The displacement bound printed in Eq. (5) is therefore $\min\{2LW_1,\,L'^2W_1^2/(2\mu_T)\}$, quadratic below the crossing and linear above it, and the generic-displacement estimate $C_4W_1^{3/2}$ that earlier versions carried is **withdrawn**. 6. **How this relates to the gap bound.** It does not improve it. Because $\ell\ge0$ implies $R_T(\theta^*_T)\ge0$, $\mathrm{Gap}_T(\theta)\le R_T(\theta)\le R_S(\theta)+LW_1$ directly, and that elementary corollary is strictly stronger than any form containing $+④$. The displacement analysis is reported as a sensitivity result about $④$ — the target-side cost of the source optimum — not as a term of the gap bound. **The term that a non-strongly-convex analysis would need, and why our earlier $C_3$ is withdrawn.** If H5 is weakened to the one-point growth inequality, non-negativity of the quadratic term $\Delta^\top H_T(\xi)\Delta\ge0$ no longer follows (take $f(x)=x^2+\epsilon(1-\cos kx)$: growth holds while $f''<0$ on a set of positive measure), a curvature term is genuinely required, and the modulus used by earlier versions of this appendix is then invalid: for symmetric $H_T$, $|x^\top H_Tx|\le\|H_T\|_2\|x\|^2$ with $\|H_T\|_2=\max(\lambda_{\max},-\lambda_{\min})$, so bounding the curvature magnitude by $\lambda_{\max}$ fails whenever a negative eigenvalue exceeds it in magnitude — with $H_T=\mathrm{diag}(-10,1)$ and $\Delta\propto e_1$, $|\Delta^\top H_T\Delta|=10\|\Delta\|^2$ against $\lambda_{\max}\|\Delta\|^2=\|\Delta\|^2$. The term is needed precisely when the direction along $\Delta$ has negative curvature, which is the case in which such an eigenvalue makes it large. The object that such an analysis would need is therefore not a spectral extreme but the negative part of the directional curvature, **for the Hessian at the relevant point of the expansion** (an endpoint evaluation is a proxy unless Lemma 7's transfer relates the two locations), $\kappa^-_\Delta(H_T)=\max\{0,-\widehat\Delta^\top H_T\widehat\Delta\}$, which vanishes exactly when $b\ge0$ and is valid without H5 or any PSD assumption; it is reported as a diagnostic in Appendix J.2, not as a theorem term. $\blacksquare$

*(Scope note: Lemma statements and the complete term-④ algebra are reproduced here so that the bound is checkable as submitted; the per-lemma proofs, the PAC-Bayes derivation behind Remark 6 and the anisotropic details of Appendix B are carried in that theory supplement, which is **not part of this release**.)*



## J.5 What §4 moved here

**(a) The displacement conditions, named in full (was §4.2).** $④=R_T(\theta^*_S)-R_T(\theta^*_T)$ is non-negative by target optimality. Two conditions must be named before it can be bounded, and both are assumptions (the checkable basin-separation certificate for the first is in J.4 step 1 (Appendix C in the released algebra)): **localization**, $\theta^*_S$ lying in the ball $B(\theta^*_T,r_T)$ on which H5's strong convexity holds — which H10 does *not* supply; and **source stationarity**, $\nabla R_S(\theta^*_S)=0$ for an interior minimiser, or the directional variational inequality $\langle\nabla R_S(\theta^*_S),\Delta\rangle\le0$, which follows from constrained optimality when $\Theta$ is convex and is an assumption otherwise. Both conditions are exact statements about minimisers, and a reproduced endpoint satisfies neither exactly.

**(b) What released checkpoints can support (was §4.2, per-cell detail).** With $\varepsilon_{\mathrm{st}}:=\|\nabla R_S(\theta^*_S)\|$ measured at the source endpoint the quadratic branch becomes $\frac{(L'W_1+\varepsilon_{\mathrm{st}})^2}{2\mu_T}$, and the linear branch becomes $④\le 2LW_1+[R_S(\theta^*_S)-R_S(\theta^*_T)]$, in which source-optimality is **replaced by a measured term** rather than assumed: the bracket is the very quantity the telescoping produces, so evaluating it *is* discharging the assumption ($\varepsilon_{\mathrm{st}}=0$ is **sufficient but not necessary**; Appendix C). **These forms are not decorative.** Over the 220 endpoint pairs of the read suite (Appendix G) source optimality holds in 59 of the 164 head-compatible pairs, the directional variational inequality in 32, and **both together in only 14** — so at computed checkpoints the exact conditions are more often false than true. The **linear** branch needs H1 and a common parameter space and nothing else — it does not use strong convexity or localization at all; the **quadratic** branch additionally needs the two-point inequality for the ordered pair, localization and source stationarity — and localization is not merely unmeasured at the measured endpoints, it is unavailable: the ball form of H5 is refuted in 220 of 220 pairs. The quadratic branch is therefore **conditional** on conditions the released checkpoints do not meet in general, and the branch a released-checkpoint measurement can bear on is the linear one; where class counts differ the head is re-initialised and neither form exists (56 of the 220 pairs). The derivation, the sharpness construction and the remaining caveats are in Appendix C steps 2–5 and Appendix J.3.

**(c) The 4.1 term-by-term reading and the elementary character of Corollary 1 (was §4.1).** The analysis uses ten numbered assumptions (H1–H10; box in Appendix J.1, usage matrix in Appendix G). It is elementary because that is what it is ($\ell\ge0$ gives $R_T(\theta^*_T)\ge0$, then Lemma 1), and we lead with it because it is **never weaker** than any form that adds a non-negative displacement term to it; the displacement analysis is therefore a statement about ④, not a term of the gap bound. Terms: ① is Kantorovich–Rubinstein-bounded at $LW_1$; ② is the optimisation residual $\varepsilon_{\mathrm{opt}}$, *contained in* $R_S(\theta)$ rather than added to it; ③ enters only the two-KR variant; ④ is the displacement cost of §4.2. Without non-negativity the two-KR comparison gives $\mathrm{Gap}_T(\theta)\le\varepsilon_{\mathrm{opt}}+2LW_1$, also displacement-free; the two forms must not be combined, since doing so charges the source risk twice. (The identity and Corollary 1 are already printed in J.1 — not duplicated here; this is the material of what earlier versions numbered §4.3.)

**(d) Algebraic restatement (was §1, moved out of the contribution bullet).** An exact decomposition (Eq. 3) whose elementary corollary is $\mathrm{Gap}_T(\theta)\le R_S(\theta)+LW_1$ — the classical additive shape — together with a **sharp** optimal-displacement sensitivity bound, $④\le\min\{2LW_1,\,L'^2W_1^2/(2\mu_T)\}$, whose quadratic branch is attained exactly. What the displacement analysis contributes is the sharp magnitude and its constant, not a tighter gap bound.

**(e) Historical narration of what earlier versions printed (was §1; this addendum also holds the *point of claim rather than in a footnote* contrast, which is dropped rather than moved — the manuscript now states that status in place in both §4 and the C1 bullet).** We state plainly that the displacement term does **not** improve the gap bound (non-negativity makes it redundant there) and that the $W_1^{3/2}$ estimate earlier versions printed is dominated at every shift. The interaction term $C_3W_1\lambda_{\max}(H_T(\theta))$ that earlier versions of this work claimed is **removed** for the two independent reasons given in J.4 (algebra in Appendix C step 5). The status, stated in place in both §4 and the C1 bullet: the bound is a *decomposition and a hypothesis generator*, not a validated theory; its curvature object is one that our own measurement-hierarchy result (§7) shows is *not measurable* under this protocol **as an off-trajectory outcome predictor** — it is measured, and reported, as a same-protocol relative diagnostic, which is the use §7.4 permits, whereas what §7 finds measurable as a proxy is a trajectory-evaluated first-order quantity — so C1 should be read as a scaffold that makes the theory–experiment gap explicit.

*(No duplication needed: the H1–H10 box is already in J.1 and the measured read-suite table already in Appendix G — the main text now points there instead of restating them.)*

# Appendix K. Campaign anchors and controls (the 2026-09-11 campaign)

## K.1 The 2026-09-11 campaign: arms, seeds and baseline anchors (moved from §8.3)

**Two cells of Fig. S3 that earlier versions listed as single-run are now seeded pairs.** On smoke→fire-smoke at 100 epochs the lr0.005 arm reads +0.10 and +0.30 pp against its same-seed `base100` baselines (seeds 43 and 44; the earlier pair carried no seed suffix and formed no seed-wise pair); on mendeley-in the `pws` arm reads −0.20 and +0.20 pp (same seeds), mean 0.00 pp, which is consistent with the loss-prior null of §6.3 rather than evidence of an effect. Both cells are now three-seed paired in Fig. S3.


**Table T11.** Supporting quantities for the three-seed readings, recomputed from the released `results.csv` best-epoch column (the same convention as §8.2's pipeline-reproduction note) rather than quoted from an earlier record of them; each row names the assertion, the quantity that carries it, and the value that quantity now takes.

| assertion | supporting quantity | value | asserted in |
|---|---|---|---|
| strong cell (smoke→SFCHD, 100 ep): *complete separation* — every lr0.005 run above every baseline run | the separation gap, min(lr runs) − max(baseline runs) | **+1.28 pp** (43.67 against 42.39) | §8.3 |
| corroborating cell (SHWD→SFCHD, 100 ep): three-seed effect size | strategy-side / paired-difference | **3.8σ** / **1.9σ** | §8.3, §9.4 |
| dota15 within-domain, 30 epochs (the non-positive counterpart cited at the same-budget control) | the two endpoints | **0.1534 → 0.1526** (−0.08 pp) | §8.3 |

The strong cell's paired three-seed gain recomputes to **+1.783 pp** (paired t = **9.44**), which is the
+1.78 pp screening reading quoted in §8.3; the corroborating cell's recomputes to **+0.51 pp**
(paired t = **3.31**, p ≈ 0.081), which is what §8.2 already prints.


**Dose–response, label budget and controls (moved from §8.3).** **Dose–response, label budget, and standard-baseline controls (2026-09-11 campaign; 52 runs, tabulated in the released record (the table numbers in circulation are T7, T8 and T10–T12)).** *Dose–response (SHWD→SFCHD, same pipeline and seed, gains in pp over the same-budget baseline).* At 30 epochs: lr 2.5× +0.86, 5× +0.87, 10× 0.00, 20× −0.76; at 100 epochs: 2.5× +0.07, 5× +0.29, 10× +0.53, 20× −0.38. The response has an interior optimum at **both** budgets and the optimum moves with the budget — 2.5–5× at 30 epochs, 10× at 100 epochs; every tier is single-seed, so this is a dose *ordering* and not a graded reading — so the registered 5× tier is a matched choice rather than a special value; the largest tested tier is negative at both budgets, bounding the escape window from above. *Label budget (100 epochs, fixed test set, train subsets of the same pool at 10/20/30/50% of labels = 1,206/2,413/3,619/6,033 images).* The baseline rises monotonically with labels (0.4128 → 0.4397 → 0.4502 → 0.4632, i.e. +5.04 pp in total, marginally diminishing), while the lr0.005 gain stays positive at every fraction (+0.51 / +0.29 / +0.70 / +1.25 pp). The 20% fraction, re-run under the current pipeline, reproduces the registered baseline and strategy values to the digit (0.4397 / 0.4426), which also confirms that no pipeline offset separates the two. With one seed per fraction the *ordering* among these four gains is not interpretable. *Standard-baseline controls.* Neither a cosine schedule at the same initial learning rate (30 ep 0.4263, +0.12 pp; 100 ep 0.4413, +0.16 pp) nor a frozen backbone (first nine modules; 30 ep 0.3757, −4.94 pp; 100 ep 0.4002, −3.95 pp) reproduces the tier effect, so it is not a schedule artefact and not available from freezing. *Layer-wise decay, measured rather than substituted.* The discriminative/layer-wise baseline that review requested — the empirical form of the discriminative-fine-tuning and gradual-unfreezing recipe of ULMFiT [41], and of LP-FT [18] — is now run directly: peak lr 0.005 with a per-layer decay factor 0.1 (stem lr 5×10⁻⁴ → head lr 5×10⁻³ over 22 layers, per-layer parameter groups; 3 seeds, same pipeline). It does **not** reproduce the gain and lands *below* the same-budget baseline: at 100 epochs 43.50 (layer-wise) vs 44.42 (uniform 5×) vs 43.91 (baseline), i.e. **−0.92 pp vs the uniform arm** (paired t = −7.24, p = 0.019) and **−0.42 pp vs the baseline** (t = −5.12, p = 0.036); at 30 epochs **−2.24 pp vs uniform** (t = −40.92, p = 0.001) and **−1.23 pp vs baseline** (t = −9.86, p = 0.010), all three seeds in the same direction. The gain therefore requires the large learning rate to be applied *globally*, not merely at the head. This agrees with the linear-network analysis of [27] (unequal layer rates help only at the initial step; equal rates are optimal afterwards) and is compatible with the non-uniform scheme of [26], which normalises the global step budget whereas this arm shrinks it (stem lr ×0.1). Three decay factors (0.03, 0.1 and 0.3) were tested at two budgets at the same peak lr, and all three land below both the baseline and the uniform arm (endpoints 0.4333/0.4083 at factor 0.03 and 0.4313/0.4003 at factor 0.3, 100/30 epochs; §9.4), so the factor-0.1 reading above is the mildest of the three.)

**Seed count of the whole 2026-09-11 campaign, stated because it bounds what these controls can show:** every campaign arm — dose tiers, label budgets, cosine, frozen backbone and AdamW — is **single-seed (shuffle-seed 42), paired against the same-seed baseline**, and its baselines are re-run under the current pipeline rather than reused from the registry; the one exception is the dota15 within-domain control carried in §8.3, which has three runs on data-order seeds **s42, s43 and s44**; the third run's directory name omits the `_s42n` suffix that the other two carry, and its seed is that campaign's fixed `--shuffle-seed 42`, recoverable from its recorded configuration and from the same convention the rest of the campaign uses — so we describe it as three seeds, and note the naming inconsistency rather than treating the run as seed-less. Its three per-seed readings are +1.12 / +0.95 / +0.93 pp, and each is owned: the suffix-less pair contributes the +1.12 pp best-epoch reading. The campaign therefore supports statement about direction and rough magnitude at that one seed, which is how we report it, and not about seed variability. **Baseline anchors for those arms** (test-split mAP50-95, same-seed baseline in brackets): dose 2.5×/5×/10×/20× at 30 epochs +0.86/+0.87/0.00/−0.76 pp (baseline 0.4219) and at 100 epochs +0.07/+0.29/+0.53/−0.38 pp (baseline 0.4393); label budgets 10/20/30/50% +0.51/+0.29/+0.70/+1.25 pp (baselines 0.4128/0.4397/0.4502/0.4632); cosine +0.12/+0.16 pp (0.4263/0.4413); frozen backbone −4.94/−3.95 pp; AdamW at 0.001/0.0025 +0.33/+0.31 pp. *(Optimiser and budget boundaries.)* AdamW at lr 0.001 / 0.0025 (100 ep) gives +0.33 / +0.31 pp with no dose–response inside that range — adaptive scaling substitutes for a higher peak learning rate at low tiers but does not reproduce the SGD dose–budget mechanism, consistent with the SGD-bounded scope of the norm-diffusion relation, which §8.5 reports as descriptive rather than calibrated. Extending the epoch budget does not help the baseline: at 200 epochs the baseline stops early at 0.4385 (best epoch 73, patience 100), within 0.12 pp of its 100-epoch value of 0.4397 (both are single runs, so we report the difference rather than a test), while lr0.005 at 200 epochs holds +0.52 pp — the gain does not decay with budget here, in contrast to the decaying budget curve of the registered pair (§8.3, budget curve). *Within-domain control for the non-SFCHD probe.* Fine-tuning dota15 pretrained weights on the dota15 target (within-domain) yields lr0.005 gains of +1.12 / +0.95 / +0.93 pp over matched same-seed baselines (per-run record: two of the three runs carry an explicit data-order seed, s43 and s44; the third is recorded without a seed suffix) (0.1614/0.1628/0.1616 → 0.1726/0.1723/0.1709; 3/3 positive, mean +1.00 pp), i.e. the same-direction effect at roughly a third of the cross-domain magnitude measured on the same target family (visdrone→dota15, +3.60 pp at ten seeds, §8.3). The within-domain arm is a same-budget control, and it cuts both ways: it shows the strategy is not *cross-domain specific*, and it is equally consistent with target **headroom** rather than domain shift being the moderator — the largest gain in the paper (+3.60 pp) occurs at the *lowest* measured shift of the graded cross-domain cells (D = 8.02) on the most unsaturated target, which is the opposite of what a shift-driven account predicts and is why we rescope the shift ordering of §5.2 to saturated targets.

---

## K.2 Structure modules and loss priors: the block readings and the screening line (moved from §8.4)

**Structure modules.** Sixteen repaired-protocol runs (eleven modules: SE/CBAM/C2fEMA/SimAM/CA/EMA/ECAplus/SA/GAM/GsConv/ADown; insertion and replacement; two protocols; checkpoint-structure-verified with parameter deltas matching the designs — the parameter-free SimAM adds zero) contain no gain ≥ +0.4 pp (range −0.41 to +0.33 pp; the +0.4 pp line is three times a typical strategy-side σ of ≈0.13 pp — the same screening logic as the frozen criterion, applied here to single-run module cells, whose noise is larger than the criterion is calibrated for); SE is consistently mildly positive (+0.12/+0.28/+0.33 pp) and below the line, and the six attention modules added in the repaired extension span −0.10 to +0.22 pp on the B-pipeline protocol. Historical reports of severe insertional degradation were invalidated by checkpoint audit and excluded. *Scope against supervision-first methods.* We do not test pseudo-labelling or labelled-unlabelled mixing routes (e.g. the sparse-label supervised loss of [24] or self-training feedback plugins); those change *what supervision enters training*, whereas the cells above hold the label budget fixed and vary only the loss prior, the module or the optimisation path. The two families are therefore complementary, and [24]'s ordering is consistent with ours.

**Loss priors (the per-cell readings the null of §8.4 is about).** sns at 100 epochs: −0.04 pp (SHWD→SFCHD, 3v3), +0.06 pp (smoke→firesmoke, 3 seeds), −0.39 pp (MAFA→mendeley, 3v3, all seeds negative, 1.5σ below criterion, paired t = −3.97, two-sided p ≈ 0.058, disclosed per protocol; a historical +0.34 pp single reading reversed sign under the corrected pipeline and is disclosed). None reaches the frozen threshold; the three *tested box-regression priors* do not exhaust the loss-design space. css fails directionally in both testable pairs (mechanism unattributed after the alignment closure); pws gains are recall-driven — the reweighting channel — and its single within-domain positive cell was removed as a pipeline-pairing artefact.

## K.3 Shift-ordering provenance, caveats and per-cell detail (moved from §5.2)

**Verbatim detail moved from §5.2 (2026-09-19).** Two caveats: the three pairs are *not* label-space-equivalent (smoke→firesmoke and smoke→SFCHD change the class vocabulary, SHWD→SFCHD does not), so D and task covary across the ordering; and the reported D values come from the released s-OTDD script at sample counts matched within each pair (Appendix K.3). **That composition confound now has a measured shape: a box-geometry $W_1$ decomposition over the same nine pairs — log-width, log-height, centre-x and centre-y — shows the shift is predominantly *scale* rather than position, the scale share being 0.757–0.952 (0.860–0.886 across the three cross-dataset pairs), so these corpora differ mainly in object size. This is a decomposition of box statistics, **not** of the s-OTDD distance: it agrees in direction with the s-OTDD ordering of §5.2 rather than decomposing it, and §5.2's ordering is therefore an ordering of that scalar, not of a physical shift. **The shift range is bounded against a measured no-shift reference:** in the same instrumentation the six within-domain pairs read D = 2.89–6.43, so the lowest cross-domain reading (7.19) exceeds the highest within-domain one by **12%**, and a second released estimator separates them by 32% (Appendix M.1). **Corpus heterogeneity behind the same read (moved from §5.2, 2026-09-19): across the ten corpora the median box area spans **1,919×** (1.88×10⁻⁴ to 3.61×10⁻¹ of image area) and the small-object share spans **0.00–0.99**; that is why composition matters beyond D, and it is a property of the corpora themselves rather than of the s-OTDD scalar (per-corpus splits and roles in Appendix L).** Ordering only; no functional claim; not in the abstract.


**(a) the within-domain r_s scope and the restated overshoot conclusion (was §5.2).** (Spearman r_s = 0.88 across pairs) and saturating overshoot as the budget extends. The within-domain channel is therefore an overshoot phenomenon whose magnitude grows with the iterative budget.

**(b) the single-run arm wording (was §5.2 within-domain).** every one of these arms is single-run

**(a) the strong-cell budget wording (was §5.2 cross-domain).**  at 100 epochs)

**(b) the disclosure wording (was §5.2 cross-domain).** disclosed as a limitation of the registered design together with the wide three-seed

**(c) the ten-seed tier wording (was §5.2 cross-domain).** analysis rules timestamped before the extension data existed) puts both cells above both thresholds at ten seeds.

**(d) the seven-seed restriction wording (was §5.2 cross-domain).** the seven seeds that were not part of the screening reading

**(a) the s-OTDD D-value provenance and released-shift-table erratum note (was §5.2 shift ordering).** and the reported D values were computed by the released s-OTDD script with the sample counts matched within each pair (12.7629 for SHWD→SFCHD at n = 5,000, 12.9893 for smoke→SFCHD at the n-matched 4,000), now recorded in the released shift table where they were previously absent.

**(b) the segment-2 comparison, tightened (was §5.2 shift ordering).** with the two segment-2 pairs sharing the same D level yet differing by a factor of

**(c) the composition-beyond-D claim, tightened (was §5.2 shift ordering).** so source-domain composition (class count, label shift) matters beyond the scalar D

**(d) the covarying-caveat wording (was §5.2 shift ordering).** so D and the task change covary across the ordering

## K.4 The norm-diffusion detail moved from §8.5 (2026-09-19)

**Norm diffusion.** Two normalisations must be kept apart: relative to the *pretrained* origin on SHWD→SFCHD (‖θ‖² ≈ 21,374), the baseline inflates by **+0.62%** at 100 epochs while the lr0.005 arm inflates by **+8.62%**, 3.2-14× across budgets, and the sns and pws arms sit within 0.1% of the baseline. Relative to *each cell's own same-pipeline baseline*, the lr0.005 inflation follows Δ‖θ‖² ≈ k·N_eff on six cells spanning N_eff = 36 to 10,530 steps (k ≈ 1.39×10⁻³ % per step). The law is descriptive, not calibrated: it is normalisation-dependent, it does not survive AdamW (the AdamW endpoint norm is released in `norm2_adamw.json`), and it is reported as a mechanism hypothesis scoped to SGD-style implicit stabilisation, not as a law (§9.4). **The endpoint norms behind the +0.62% and +8.62% figures above are released in `norm2_extra.json`, so both recompute directly from the released values.

## K.5 Positive controls: what bounds the nulls of §8.4 (2026-09-19)

The nulls of §8.4 are statements about detection. Four controls on the same pipeline, target family and protocol fix the range in which such a null is informative rather than merely unmeasured.

1. **Deliberate degradation is detected from below.** The layer-wise-decay schedule at the same peak learning rate lands below both the same-budget baseline and the uniform arm at every factor tested: 0.4333/0.4083 (factor 0.03) and 0.4313/0.4003 (factor 0.3) at 100/30 epochs, against baseline 0.4396 and uniform 0.4426 (§9.4, arm detail in K.1).
2. **Configuration-scale changes read far outside σ.** Frozen backbone −4.94/−3.95 pp; label budgets 10/20/30/50% +0.51/+0.29/+0.70/+1.25 pp; cosine +0.12/+0.16 pp; AdamW +0.33/+0.31 pp (2026-09-11 campaign arms, all single-seed, per-arm anchors in K.1).
3. **A same-pipeline second architecture resolves both sides of the screening line.** YOLO11n +1.27 pp (t = 6.97, p = 0.020) at 30 epochs and −0.01 pp (t = −0.10, p = 0.93) at 100 epochs on the same pair (§8.3); **its DOTA15 runs are not read against the third cell** (different three-way split and initialisation — see §8.3).
4. **The headline effect is reproduced within a domain.** dota15→dota15 (within-domain) +1.12/+0.95/+0.93 pp over matched same-seed baselines at seeds s42/s43/s44 (three runs; the s42 run's directory name omits the seed suffix, and its configuration records `--shuffle-seed 42`).

**What these controls do not do.** They bound what the instrument resolves at the *large* end; they do not lower the detection floor of the nulls themselves, which stays at 0.56–0.62 pp for a three-seed paired test at the observed σ, and at +0.4 pp by construction for the single-run module screens. Every control above except the within-domain arm is single-seed, so none of them stands in for the multi-seed evidence that a positive claim in §8.4 would require. That asymmetry is why the module block is reported as a bounded negative rather than as evidence of absence.

## K.6 The budget curve in full (moved from §8.3, 2026-09-19)

**Budget curve.** For SHWD→SFCHD the gain decreases in its point estimates across budgets and then plateaus — +1.00/+0.65/+0.51 pp at 30/50/100 epochs (every point a full 3v3) and +0.52 pp at 200 epochs (single run, Appendix K.1) — so point-estimate monotonicity is claimed over 30→100 epochs and a plateau, not a continued decline, beyond it; per-seed monotonicity is not claimed. The smoke→SFCHD pair is direction-consistent at 30/50 epochs but ungraded (single runs).

# Appendix L. Corpus roles, provenance and per-corpus split statistics (moved from §8.1)

**The per-corpus attribute ranges behind §5.2 (released `08_数据属性_扩展变量.csv` (the per-corpus attribute table), 26 rows of domain × split).** Across the ten corpora: median box area **1.88×10⁻⁴ … 3.61×10⁻¹** of image area (a **1,919×** span), small-object share **0.00 … 0.99**, empty-image ratio **0.00 … 0.61**, and boxes per image **0.49 … 139.9**; on the 20% subsets the median box area spans 7.4×10⁻⁵ … 7.8×10⁻². These are the release's own per-corpus attributes, printed here because §5.2's scale-dominance reading rests on the corpora differing mainly in object size; the extended variables are not a substitute for the pairwise distances of §5.2.


**Corpus-by-corpus roles and provenance (moved from §8.1; Table S1, in the supplementary material, carries the pairs, and **Table L1 below** carries the per-corpus splits).** Each corpus enters through one of three roles — source pretraining, same-object fine-tuning (7 pairs), or cross-domain fine-tuning — and the shift between roles is quantified in §8.2 (s-OTDD). The five cross-domain pairs are MAFA→mendeley, MAFA→mask and smoke→firesmoke (B pipeline) together with **SHWD→SFCHD and smoke→SFCHD (SFCHD pipeline)**, the latter two being the pairs that carry the paper's only criterion-passing cells. Mendeley is also the source endpoint of the mendeley target pair. The masked-face corpora (mafa, mask_clean, mendeley) are the low-shift end and the aerial corpora (DOTA, VisDrone, AI-TOD) the high-variance end, by box statistics and images per box (released `08_数据属性_扩展变量.csv`, the same table). Two provenance statements in place of citations we cannot establish: the five corpora marked "as recorded in the released registry" were obtained from public bundles (Kaggle, Roboflow/Mendeley packaging) whose exact provenance is recorded in the registry rather than in a citable publication; and MAFA is used here as a masked-face *source* corpus, as packaged with the mask detectors we compare against, not as the recognition benchmark of [38] — we flag the difference rather than imply identity. One distinction that an earlier version of this table got wrong and that we state explicitly because it is a confound if left implicit: the **smoke corpus is single-class** (`nc = 1`, "smoke") while the **firesmoke corpus is two-class** (fire, smoke); the smoke→SFCHD line therefore starts from a *single-class* source head and is adapted to the target's two classes (Appendix D), and the released weights record both stages (`smoke_pretrain.pt`, `nc = 1`; `smoke_pretrain_nc2.pt`, `nc = 2`). We report both endpoint conventions for that cell where relevant and do not describe the adaptation as free of effect. Per-corpus split statistics (images, boxes, boxes/image, empty-image ratio, median box area, small-object ratio) are released with the per-run tables, and Table S1 maps them onto the thirteen pairs together with the measured shift D.

**Scope of this table.** Table L1 covers the ten corpora that carry the pretraining, same-object and cross-domain roles of §8.1; the four further target corpora used by the label-axis and clean-protocol subsections (**`neu_det`, `gdut_hwd`, `chv`, `fsin`**) are described where they are first used and are deliberately not given roles here. **Table L1 — the ten corpora, by role and split** (this table was moved out of §8.1 to keep the main text inside the journal's page rule; the main text points here).

| corpus | content | classes | train (20% subset) | test/val | source |
|---|---|---|---|---|---|
| SHWD [33] | safety-helmet wearing, industrial and construction scenes | 2 (hat, person) | full source split | own test split | public dataset (GitHub) |
| SFCHD [34] | safety clothing and helmet detection | 2 (hat, person) | 2,413 (20% of source) | 6,033 | public dataset (arXiv:2306.02098) |
| smoke (keremberke) | smoke-only imagery | 1 (smoke) | 15,096 | 2,160 | Kaggle corpus (Roboflow COCO→YOLO), as recorded in the released registry |
| firesmoke | fire and smoke, cleaner packaging | 2 (fire, smoke) | 56,161 (11,232) | 6,411 | as recorded in the released registry |
| mafa | masked faces | 1 (face mask) | source-pretraining corpus | own split | as recorded in the released registry |
| mask_clean | face masks | 1 (face mask) | 6,120 (1,224) | 919 | as recorded in the released registry |
| mendeley | face masks | 1 (face mask) | 5,750 (1,150) | 800 | as recorded in the released registry |
| VisDrone [35] | UAV aerial scenes, pedestrian/vehicle | 10 | 6,471 (1,294) | 1,610 | public dataset (TPAMI) |
| DOTA v1.0 [36] / DOTA-v1.5 | aerial imagery | 15 / 16 | 1,411 (282) | 458 | public dataset (CVPR 2018) |
| AI-TOD [37] | aerial tiny objects | 8 | 11,214 (2,243) | 2,804 | public dataset (ICPR 2021) |


# Appendix M. Method, protocol and framework detail moved from the main text (2026-09-19)


Nothing here is new: every subsection below is the **verbatim** text that the main text of this
version moved into the supplementary material so that the article file fits the journal's page range.
Each main-text pointer names its subsection, and no claim, number or disclosure was altered in the move.


## M.1 The setup in full: task, metrics, shift quantification, flatness and notation (moved from §3)

**The s-OTDD floor, on both released computations.** *(i) The feature-level table behind §5.2's D values* (ResNet-18 features, 4,000 samples, sliced Wasserstein, s-OTDD = √(W₂² + label term)) gives nine pairs: within-domain 2.8905 (DOTA15), 3.3524 (AI-TOD), 3.5071 (mendeley), 5.7532 (firesmoke), 6.0521 (mask), 6.4273 (VisDrone); cross-domain 7.1894 (MAFA→mask), 9.4395 (smoke_ker→firesmoke), 13.0313 (MAFA→mendeley). The lowest cross-domain reading therefore exceeds the highest within-domain reading by **12%** (7.1894 / 6.4273 − 1 = 0.119). *(ii) The earlier release computed with a different estimator* (`otdd_results.csv`) gives within-domain 2.6593 (Paddle subsample), 3.4159 (SFCHD), 7.4686 (SHWD subsample) and cross-domain 9.865 (SHWD vs Paddle), 11.51 (fusion vs SFCHD), 12.7629 (SHWD vs SFCHD), i.e. a floor margin of **32%** on that computation as well. Both are stated because the two estimates are not interchangeable: what the floor supports is that D separates shift from a measured no-shift reference at these two instrumentations, not that the two scales coincide.


### 3.1 Task and evaluation metrics

Object detection requires, for every object of interest, a localisation (bounding box) and a classification decision. Accuracy is summarised by mAP. We report **mAP50** (detection; accepts IoU ≥ 0.5) and **mAP50-95** (localisation tightness; averaged over IoU 0.50–0.95 with 101-point interpolation and `max_det = 300` detections per class per image, the Ultralytics default). The per-cell mAP50 column is carried in Table T12 below, because the two metrics can move in opposite directions at long budgets (§5.2, §8.5). All experiments use YOLOv12n [10] unless a second architecture is named explicitly — the only exception is the YOLO11n control of §8.3, added because one architecture cannot separate an optimisation effect from an architectural one.

### 3.2 Quantifying domain shift

With $\mu_S,\mu_T$ the source/target data distributions, our primary shift measure is the 1-Wasserstein distance

$$W_1(\mu_S,\mu_T) = \inf_{\pi\in\Pi}\int \|z-z'\|\,d\pi(z,z'), \tag{1}$$

over couplings with the given marginals. Empirically we use a sliced, label-aware estimator over frozen backbone features — sliced 1-Wasserstein geometry (Bonneel et al. [22]) combined with the label-aware dataset distance of Alvarez-Melis & Fusi's OTDD [9], henceforth s-OTDD — decomposed into feature and label terms. The bound of §4 uses this population distance; the measured D is its practical proxy on frozen features, and the constants are *not* calibrated, so the experiments bear on the *form* of the geometric interaction (through the flatness proxies of §4.2 and §7), not on numerical tightness.

### 3.3 Flatness (and its protocol)

For parameters $\theta$, the flatness on domain $D$ is the worst-direction loss increment

$$S_D(\theta) = \max_{\|\epsilon\|\le \rho\|\theta\|}\;[L_D(\theta+\epsilon)-L_D(\theta)], \tag{2}$$

where the radius is **relative to the parameter norm** ($\epsilon = \rho\|\theta\|\hat v$; $\rho \in \{0.001, 0.003, 0.01\}$, primary 0.001; $\|\theta\| \approx 148$–158 in our runs, $\|\theta\|^2$ recorded per model). Near a stationary point $S_D \approx \tfrac{\rho^2\|\theta\|^2}{2}\lambda_{\max}(H_D)$; at non-stationary points the increment is first-order dominated, $S_D \approx \rho\|\theta\|\,\|\nabla R_D(\theta)\|$ — a slope/distance proxy, verified by the ε-scaling decomposition of §7.2(1) and central to the measurement-hierarchy proposition.

### 3.4 Notation

$\mu_S,\mu_T$; $\theta$ (any parameter value); $\theta_{\mathrm{src}}$ (source-training endpoint, the fine-tuning initialisation); $\theta_{\pi,T}$ (endpoint after strategy $\pi$ for $T$ epochs); $\theta^*_S,\theta^*_T$ (population optima); $R_S,R_T$; $W_1$; $S_D$; $\eta,T$; $\mathrm{Gap}_T(\theta)=R_T(\theta)-R_T(\theta^*_T)$; $\Delta_\pi(T)$ (strategy gain); $\Sigma$ (saturation diagnostic: baseline gain at 100 ep minus baseline gain at 30 ep). Loss variants: **sns** (scale-normalised Shape-IoU [11]), **css** (centred-scale Shape-IoU), **pws** (prior-weighted Shape-IoU). **3v3** = three-seed-by-three-seed fully-permuted paired runs. Gains are in percentage points (pp) of mAP50-95 unless stated, always same-budget and same-pipeline.


## M.2 The joint bound in full: decomposition, corollary, proposition and their conditions (moved from §4)

Three statements: an exact decomposition with its **elementary** gap corollary (§4.1); a **sharp**
sensitivity bound on the optimal-displacement cost (§4.2) that does **not** improve that corollary; and a
**negative result** — the curvature term this decomposition invites is redundant under the paper's own
strong-convexity assumption, and where curvature is genuinely needed the standard top-eigenvalue modulus is
invalid, the correct object being the path quantity $\kappa^-_\Delta$ (**Appendix J.4**). The bound is **not
a validated theory**: no graded claim in this paper rests on it. Derivations, the term-by-term reading of
Eq. (3) and the hypotheses H1–H10 are in **Appendix J**.

### 4.1 The decomposition, and the elementary gap corollary

The gap telescopes exactly for *any* parameter value θ:

$$\mathrm{Gap}_T(\theta) = \underbrace{[R_T(\theta)-R_S(\theta)]}_{①} + \underbrace{[R_S(\theta)-R_S(\theta^*_S)]}_{②} + \underbrace{[R_S(\theta^*_S)-R_T(\theta^*_S)]}_{③} + \underbrace{[R_T(\theta^*_S)-R_T(\theta^*_T)]}_{④}. \tag{3}$$

> **Corollary 1 (gap bound; elementary).** Under H1 and non-negativity $\ell\ge0$ (both by construction for
> detection),
> $$\mathrm{Gap}_T(\theta)\;\le\;R_S(\theta)+LW_1 . \tag{4}$$

### 4.2 The sharp optimal-displacement sensitivity

Term ④ is non-negative by target optimality, but bounding it needs two further conditions on the source
minimiser — **localization** and **source stationarity** — neither of which holds at a computed checkpoint
(**Appendix J.5(a)**).

> **Proposition 1 (optimal-displacement sensitivity; sharp).** Under H1, H2, H5 in its two-point form and
> the two conditions above,
> $$④\;\le\;\min\Bigl\{2LW_1,\;\frac{L'^2}{2\mu_T}W_1^2\Bigr\}, \tag{5}$$
> the **quadratic** branch binding below $W_1=4L\mu_T/L'^2$ and the **linear** one above it. Its constant
> $1/(2\mu_T)$ is attained with equality: the branch is **sharp**.

The **linear** branch needs H1 and a common parameter space and nothing else; the **quadratic** branch is
**conditional** on those two conditions, which the measured endpoints do not meet — the ball form of H5 is
refuted in 220 of 220 endpoint pairs, and where class counts differ the head is re-initialised and neither
branch exists. Derivation and remaining caveats: Appendix J.3 and Appendix G.


## M.3 The protocol in full: settings, seed layers, registration status and the clean-protocol specification (moved from §8.1)

**Figure and table numbering.** Figures are numbered F1–F7 and tables T1–T12 in the released material; in this submission the article carries one figure, **Fig. 1**, the two-stage protocol schematic. The figures **carried here** use **supplementary numbering — Fig. S1 to Fig. S5**, (budget curve, shift ordering, dual-metric separation, measurement-hierarchy schematic, prediction–evidence–status matrix); **none of the five is cited from the main text** as the article stands, so this numbering is internal to the supplement. The released **F3** (shift ordering) and **F5** (the detector family and its insertion points) are carried here but are **not cited** in either text, and are therefore not numbered. The design table of §8.2 is **Table S1** (the thirteen domain pairs). Of the released tables, **T10** is cited in **this supplement only**, **T11** is cited in this supplement and **T12** in the accounting behind C4, which is also part of this supplement, and the remaining table numbers (T1–T6 and T9) belong to the released record and to earlier numbering; the tables that exist in this submission are **T7**, **T8**, **T10**, **T11** and **T12**, together with **Table S1**. **Datasets (introduced here, cited where a canonical source exists).** Thirteen domain pairs are built from ten image corpora, listed in Table S1 by pair; the per-corpus table, with the split sizes actually used (20% subsets in parentheses), is **Table L1 of the supplementary material (Appendix L)**, which also carries the corpus roles, provenance and the per-corpus split statistics.

One confound is stated in the main text because it conditions a headline cell: the **smoke corpus is single-class** (`nc = 1`, "smoke") while the **firesmoke corpus is two-class** (fire, smoke), so the smoke→SFCHD line starts from a *single-class* source head adapted to the target's two classes, and the released weights record both stages (`smoke_pretrain.pt`, `nc = 1`; `smoke_pretrain_nc2.pt`, `nc = 2`); we report both endpoint conventions for that cell and do not describe the adaptation as free of effect. The three corpus roles, the cross-domain pair list, the shift ends, the provenance statements and the per-corpus split statistics are in **Appendix L**.

**Two labels the released registry keys runs by, defined here once.** *A pipeline* and *B pipeline* are the two training stacks: A carries the SFCHD-side cells and takes an explicit augmentation-RNG seed (`a5_train_obj_aug.py`, built on the registered trainer), while B is the registered stack (`train_obj.py`, ultralytics 8.4.120). They differ in that augmentation control and in framework bookkeeping, so cross-pipeline *magnitudes* never enter a graded contrast — every graded contrast is same-pipeline — and a cross-pipeline number appears only where it is labelled as such: the one order-of-magnitude remark of this kind is flagged in place (§8.2) and carries no graded weight. The seed mechanism is a dual layer — a `--shuffle-seed` data-order permutation, which is what the registered σ varies, plus a separate `--aug-seed` augmentation-RNG layer. A run recorded **without** a seed suffix is *unseeded*: no `--shuffle-seed` permutation was passed, and because the framework's own `seed` argument is not consumed by the data pipeline on these datasets (**Appendix D**), such a run has no declared data order — a comparison against it is therefore a strategy-versus-baseline contrast at one order, not a seed-wise pair — and the registry's naming conventions, including the *BoxB* label and the two-stage protocol these stacks implement, are in **Appendix D**; the one mapping fact the argument needs is stated here: **for the two SFCHD cells both keys point at the same physical directory**, so the reported metric is measured on the split that selects the checkpoint — as for the `aitod_20p`, `dota15_20p`, `dota_20p` and `mende_20p` cells and the source-stage yaml, while `mask_20p`, `firesmoke_20p` and `visdrone_20p` carry a genuine held-out test split. Training and evaluation are disjoint at the image level in every case, so this is not train/test contamination. **For all seven of these cells the clean three-way protocol replaces that endpoint rule with the corpus's own held-out split; the per-cell readings are in Appendix M.5.**

**The two rates, and why the baseline one is the one it is.** The baseline arm's peak learning rate is 0.001 and the strategy arm's is 0.005 — the 5× of the abstract; the dose axis of §8.3 (2.5×/5×/10×/20×) is expressed as multiples of that baseline, so a multiplier always means a multiple of 0.001, and the released registry labels arms accordingly (`@lr0.001` for baseline-rate arms, `lr005` for the strategy). This paper does not derive 0.001 from a criterion; what it does establish is that 5× is **not** a specially favourable point on the axis — the measured dose response has an interior optimum at both budgets, and the optimum *moves with the budget* (2.5–5× at 30 epochs, 10× at 100 epochs, §8.3) — so the registered tier is a matched choice rather than the best one.

**Pre-registration and registration status.** Blinded dual-model predictions were written before any outcome data existed (repository timestamps 2026-09-02), and the grading criteria were fixed in the internal grading documents of 2026-09-04/05 — after the first same-pipeline observations of the headline cells but before their final 3v3 completions, and never changed afterwards. The freezing timeline, its consequence (the registration postdates those first observations, so we call it "prospectively frozen" rather than "pre-registered"), and the retraction of the registration-time family-control claim are stated below. All documents carry repository timestamps; none were back-dated.

**How the clean protocol was specified, and what it holds fixed.** The three-way protocol was built on 2026-09-14, after the screening measurement that selected these two cells and before any clean-protocol run. Its runs are a separate batch from the published ones, driven by yaml files written by that same carve builder; individual launch times are not preserved in the release — the archive's file times are retrieval times — so the ordering just stated rests on the builder's timestamp and not on per-run timestamps. Within a cell the seeds share one source checkpoint — the release records it per run, together with the deterministic data-order seed — so initialisation is fixed by design rather than varied, and the initialisation component of the variance is measured separately, on independent source endpoints. What the protocol changes is the endpoint rule and not the arm pairing: the reported value is the target corpus's own held-out test split, which no checkpoint selection can touch, whereas the checkpoint itself is chosen on the validation carve-out taken from the remaining training pool.


## M.4 The pair construction and the statistical framework in full (moved from §8.2)

Table S1 lists the thirteen domain pairs studied: seven within-domain pairs; three B-pipeline cross-domain pairs (disjoint datasets); **two SFCHD-pipeline cross-domain pairs, SHWD→SFCHD and smoke→SFCHD**; and one post-freeze directional probe (visdrone→dota15). Eight of the ten B-pipeline target domains are saturated at 30 epochs (Σ ≈ 0); the two small-sample pairs (dota15/dota) are not. Shift D is quantified by s-OTDD over frozen features (4,000–5,000 samples/split). The thirteen pairs, their roles and their measured shift — with the two columns that say what each row can carry, because the table is a design table and not an evidence table: "LR arm paired" is `no` wherever a cell has a single arm per side, and the tier column is this paper's own grading (*screening* = three-seed reading under the frozen rule, *replication* = the outcome-selected ten-seed extension and its reuse-free seven seeds, *directional* = post-freeze probe, *ungraded* = single-run points used in no graded claim, ***clean census*** = the clean three-way re-run of the same seven within-domain cells at a held-out endpoint, three seeds each and ten for two of them, which likewise enters no graded or family-level claim and whose per-cell values are in Appendix M.5):

| # | pair | category | budgets with paired seeds | registered seeds | D (s-OTDD) | LR arm paired (seeds) | evidence tier |
|---|---|---|---|---|---|---|---|
| 1 | aitod→aitod | within-domain | 30 | 1 | 3.35 | no (1); clean 3 (s42–s44) | ungraded; **clean census (n=3)** |
| 2 | dota→dota | within-domain | 30 | 1 | n.m. | no (1); clean 3 (s42–s44) | ungraded; **clean census (n=3)** |
| 3 | dota15→dota15 | within-domain | 30, 100 | 1 | 2.89 | no (1); clean 10 (s42–s51) | ungraded; **clean census (n=10) — a null at 30 ep, negative at 100 ep** |
| 4 | firesmoke→firesmoke | within-domain | 30, 50, 100 | 1–3 | 5.75 | no (1); clean 3 (s42–s44) | ungraded; **clean census (n=3)** |
| 5 | mask→mask | within-domain | 30, 50, 100 | 1–3 | 6.05 | no (1); clean 3 (s42–s44) | ungraded; **clean census (n=3)** |
| 6 | mendeley→mendeley | within-domain | 30, 50, 100 | 1–3 | 3.51 | no (1); clean 3 at 30 ep, 10 at 100 ep | ungraded; **clean census (n=3 / n=10)** |
| 7 | visdrone→visdrone | within-domain | 30 | 1 | 6.43 | no (1); clean 10 (s42–s51) | ungraded; **clean census (n=10) — robustly negative** |
| 8 | smoke→firesmoke | cross-domain (B) | 30, 50, 100 | 1–3 | 9.44 | partly (1–3) | ungraded |
| 9 | mafa→mask | cross-domain (B) | 30, 100 | 1 | 7.19 | no (1) | ungraded |
| 10 | mafa→mendeley | cross-domain (B) | 30, 50, 100 | 1–3 | 13.03 | partly (1–3) | ungraded |
| 11 | SHWD→SFCHD | cross-domain (SFCHD) | 30, 50, 100 | 3, 10 | 12.76 | yes (3 → 10) | **replication** (corroborating) |
| 12 | smoke→SFCHD | cross-domain (SFCHD) | 100 | 3, 10 | 12.99 | yes (3 → 10) | **replication** (strong) |
| 13 | visdrone→dota15 | post-freeze probe | 100 | 10 | 8.02 | yes (10) | *directional* |

(n.m. = not measured for that pair; the remaining within-domain pair shares its object's row. The four pairs registered for the prospective replication of §1 are **not** reported as results in this paper; those readings belong to the replication, and the roster of the four is in Appendix I, alongside their shift readings.)**On SHWD→SFCHD's two roles**: its source endpoint was trained under the A pipeline, so its *absolute* magnitudes are order-comparable with B-pipeline values only, while its *cell contrast* — lr0.005 against lr0.001 from the same source endpoint, same target subset, same budget, same seeds — is same-pipeline in the sense that matters for the paired test, and it is on that contrast, not on a cross-pipeline magnitude comparison, that the corroborating cell's evidence rests. We therefore treat it as a registered family cell for grading and as a cross-pipeline reference for magnitude comparisons, and the phrase 'reported separately' is withdrawn. The registered family** — what can and cannot be reconstructed from the released material, and the 26-vs-28 discrepancy — is set out in **Appendix I**, where the roster is enumerated cell by cell and the consequences are stated; this paper uses that 26-configuration roster for every family-level quantity and never uses the recorded count of 28 as a denominator.

**Statistical framework, in one paragraph.** The confirmatory content is the fresh-seed paired tests on the two screening-selected cells: both tiers report the **paired sign-flip permutation** alongside the paired t, and permutation is the primary test, with its n-dependent floor ($2/2^n$) printed with every value so that a floor-limited p cannot be read as strong evidence. The family-level analysis — paired t-tests on the 26 configurations of Appendix I (Table T10) with Benjamini–Hochberg at q = 0.05 (Bonferroni, α/m = 1.9×10⁻³, as sensitivity) — is a *robustness* read and not a family-wise guarantee, because the roster was enumerated after the outcomes and the extension was itself triggered by the screening result. "The frozen criterion" is the frozen effect-size rule stated below, frozen before the final outcomes: a cell passes when the mean 3-seed gain exceeds 3× the strategy-side seed σ; its role is *screening and tier assignment*, and its null behaviour is derived in Appendix F. Under it the registered tier is a screening result (BH q = 0.29 and 1.00), decisive only in the pre-specified ten-seed extension and on the seven fresh seeds (BH q = 1.7×10⁻⁸/8.1×10⁻⁵ and 4.9×10⁻⁶/1.0×10⁻³); that extension is outcome-selected, which no multiplicity correction repairs. The full statement is in **Appendix F.1**.

## M.5 The clean three-way protocol beyond SFCHD: the per-seed readings

**Why this subsection exists.** §M.3 specifies the clean three-way protocol for the two SFCHD cells. The same carve-out builder was also run over the seven within-domain corpora and over two cross-domain pairs that do **not** involve SFCHD, so that §8.3's sign structure can be read on targets outside the registered family. This subsection carries those per-seed values, and the two released files named in §8.3 (`clean_threeway_perseed.csv`, `clean_threeway_summary.csv`) recompute every number printed here.

**What is held fixed, and what the endpoint is.** For every cell the training split is the same 20%-label subset as the published runs; the validation split is a carve-out taken deterministically (seed 42) from the remaining training pool; and the reported value is the target corpus's **own held-out test split**, so no checkpoint selection can touch the reported split. The endpoint is mAP50-95 (%) of `best.pt`, the checkpoint selected on the carve-out; `last.pt` is carried in the release as a robustness column and agrees in sign throughout, including the negative cell below. Split sizes were re-measured for this submission, and every pairwise **name-level intersection is zero** (train / validation carve-out / test): 2243/1000/2804 (aitod20), 282/300/458 (dota15_20p), 282/300/458 (dota_20p), 11232/2000/6411 (firesmoke20), 1224/900/919 (mask20), 1150/1000/800 (mende20), 1294/500/1610 (visdrone_20p). Both arms are this paper's own — baseline lr 0.001 against strategy lr 0.005 — so each row is a same-pipeline, same-budget, same-seed pair.

**The 30-epoch within-domain cells: two arms × three seeds, and ten seeds for two of them.** Δ = strategy − baseline, in pp; p is the paired sign-flip permutation, which is the primary test, printed with its n-dependent floor. The two cells carried to ten seeds are the ones the extension was spent on: dota15 because it carried the smallest effect at three seeds, and visdrone because it is multi-class (ten classes) — so that the extension is not an extension over single-class corpora.

| cell | baseline (mean ± σ) | strategy (mean ± σ) | Δ | seeds won | paired t | p (permutation) | floor |
|---|---|---|---|---|---|---|---|
| aitod20 | 10.398 ± 0.180 | 9.488 ± 0.474 | −0.909 | 0/3 | −5.34 | 0.25 | 0.25 |
| dota15→dota15 **(10 seeds)** | 15.214 ± 0.118 | 15.183 ± 0.539 | **−0.031** | **7/10** | −0.17 | 0.871 | 0.00195 |
| dota→dota | 17.169 ± 0.188 | 16.234 ± 0.351 | −0.935 | 0/3 | −3.59 | 0.25 | 0.25 |
| firesmoke→firesmoke | 39.581 ± 0.389 | 35.197 ± 1.139 | −4.384 | 0/3 | −6.23 | 0.25 | 0.25 |
| mask→mask | 65.348 ± 0.602 | 64.415 ± 0.909 | −0.933 | 0/3 | −1.49 | 0.25 | 0.25 |
| mendeley→mendeley | 73.075 ± 0.278 | 70.171 ± 2.276 | −2.903 | 0/3 | −2.52 | 0.25 | 0.25 |
| visdrone→visdrone **(10 seeds)** | 11.681 ± 0.108 | 10.872 ± 0.354 | **−0.809** | **0/10** | −7.66 | **0.00195** | 0.00195 |

**The 100-epoch cells: two arms × ten seeds.** The first two rows are cross-domain; the third is within-domain. **A permutation $p$ cannot fall below its floor** ($2/2^{n}$: 0.00195 at $n=10$), so where a contrast is more extreme than the floor the table prints the floor; the paired-$t$ $p$ for that contrast would be $3.2\times10^{-11}$, and it is **not** a permutation result.

| cell | category | baseline (mean ± σ) | strategy (mean ± σ) | Δ | seeds won | paired t | p (permutation) | floor |
|---|---|---|---|---|---|---|---|---|
| aitod→visdrone | cross-domain | 10.209 ± 0.116 | 10.397 ± 0.110 | +0.188 | 9/10 | 3.30 | 0.0059 | 0.00195 |
| visdrone→dota15 | cross-domain | 11.626 ± 0.167 | 15.277 ± 0.253 | +3.650 | 10/10 | 37.75 | **0.00195** (= the floor) | 0.00195 |
| mendeley→mendeley | within-domain | 72.549 ± 0.488 | 70.230 ± 1.411 | −2.319 | 0/10 | −5.69 | 0.0020 | 0.00195 |

**What this carries, and what it does not.** Three limits are stated rather than left to the reader. First, five of the seven 30-epoch rows rest on n = 3, where the permutation floor is 2/2³ = **0.25**, so those five cannot reach a conventional level however large their mean shift: they are a **sign census with seeds**, not a significance claim, and the floor is printed beside every p for exactly that reason — the same distinction §8.2 draws for the screening tier. Second, the two cells carried to ten seeds are the only 30-epoch rows with the power to separate an effect from noise, and they separate in opposite directions — visdrone clears the conventional level at the floor, dota15 does not come near it — which is the point of having spent the extension on those two rather than on the largest effects. Third, the cross-domain evidence here is **two cells**, not a family: both are positive and both clear the conventional level, but two cells support a sign reading on targets outside SFCHD and not a broader population claim.

**The two cross-domain cells of this table are shared-training cells, stated as a fact.** Every row of this table is this paper’s own run, with one qualification at the claim: for `visdrone→dota15` the training recipe and the training set are **shared with the companion paper on evaluation validity** (its `T1-c`), and the two papers compute their readings separately under their own selection and endpoint rule. The fingerprint comparison shows the epoch-1 training columns agree bit-for-bit while the epoch-100 columns differ in the fourth and fifth decimal, so what the two papers hold is **one recipe, one training set and seeds, one implementation, run twice — a run-level reproduction**; **neither paper describes it as a cross-implementation replication.** The two papers’ values for this cell differ by **0.077 pp (≈2%)**, and that difference conflates run-level reproducibility with the endpoint-rule difference: **we do not attribute it to either**, since separating the two would require re-running both under a single endpoint rule. The same qualification applies to `aitod→visdrone`; the within-domain rows above are not shared.

**Reading.** Six of the seven within-domain cells are negative at 30 epochs and one — dota15, at ten seeds — is a **null** (7 of its 10 seeds favour the strategy arm); the within-domain cell read at 100 epochs is negative in all ten; and both cross-domain cells are positive, nine of ten and ten of ten. The dota15 row is reported as a null rather than folded into the census, because at three seeds its mean (−0.21 pp) was indistinguishable from the noise the extension then measured (−0.03 pp): the extension did not weaken the pattern so much as show which part of it was noise. This is the two-channel structure §8.3 reports, measured at a held-out endpoint on targets that do not include SFCHD. It does not enter the registered family of Appendix I and no family-level quantity uses it.

**Provenance.** These runs are a separate batch from the published ones: the registered stack (`train_obj.py`, ultralytics 8.4.120) with the `shapeiou` loss, each run driven by its own `*_3way.yaml` and recorded per run in the released per-seed file together with its two arms and its data-order seed. The batch follows the carve builder's timestamp of 2026-09-14T07:37Z and precedes the held-out readout of 2026-09-20; individual launch times are not preserved in the release, so the ordering rests on those two timestamps and not on per-run times.

# Reference-status ledger: metadata corrections and the five anchor classes (moved from the References section)



**The article's References-section ledger, moved here (2026-09-19) so that the article carries the plain list a reviewer expects.**

> ⚠ **2026-10-02 状态说明（重要，2026-10-04 补充）**：本台账（以及本补材正文里所有形如 `[31]` 的方括号编号）属于**上一版稿子的 74 条编号表**，与**现稿** `P1_NewDraft_v1_20260927.md` 的参考文献表（**2026-10-03 起为 `[1]`–`[29]` 的编号制**，2026-10-04 补入 `[30]`–`[39]` 后为 **39 条**）**不是同一套编号**：例如本台账的 `[31]`（谱估计所用的 Lanczos 参考）在现稿里是 `[31]` He et al., ICCV 2019。
> **⇒ 补材里的方括号编号一律读作"本台账的编号"，不得与正文编号互相引用。** 本台账保留为**历史记录与元数据核验证据**。
 The reference list, [1]–[74], is carried in **the article's own References section** as the numbered list, with each entry's status marker (`[verified]` / `[preprint]`) printed inline and the evidence behind each marker recorded in the ledger below (the few-shot-detection and fine-tuning anchors cited in §2 and §8.4 extend the original run); each entry carries a status where one has been recorded — `[verified]` (volume/issue/pages or DOI re-checked against OpenAlex) or `[preprint]` (arXiv only). **74 of the 74 entries carry such a marker — 31 `[verified]` and 43 `[preprint]` — after a second-source pass over the 21 that earlier versions listed as unchecked; each marker names its evidence (a DOI, a venue and year, or an arXiv identifier) rather than asserting coverage, and the per-entry evidence is recorded in the supplementary reference-status ledger.** Every entry that earlier versions recorded as untraced or retired has been dealt with in the consolidation: the retired placeholder slot is gone from the list, and the entry no source could resolve is replaced by a verifiable calibration anchor. No unresolved placeholder marker remains. The anchors are verified across five classes — OT/DA theory, flatness/PAC-Bayes, fine-tuning and optimisation, DA-detection and flatness-DG, measurement and reproducibility — whose individual names, and the metadata corrections made in this version ([22] and [2]), are recorded in the supplementary reference-status ledger.

**Reference-metadata corrections made in this version (the details the main text now records by index only).** Two metadata corrections survive the consolidation and are recorded here: Bonneel et al. [22] is JMIV 51(1):22–45 (2015), not 43(3):315–328; and Redko et al. [2] is the ECML-PKDD 2017 analysis, the earlier venue string ("PACML 2017") having proved untraceable. Three further corrections that earlier versions of this ledger carried — the Redko et al. TPAMI entry, the Mulayoff & Michaeli ICML entry, and the Cross-Domain Adaptive Teacher entry — **no longer have an object**: those entries were merged into cluster citations or removed from the list in the consolidation recorded under the status convention below, so there is no longer an index for them to correct. The `[preprint]` convention means arXiv only, with no volume/pages to check.

**Anchors verified across five classes, citation by citation.** Every index below is checked against the list as consolidated; the anchor classes are rebuilt from the entries the list now contains, and entries that earlier versions of this ledger named are either carried here under their present index or were removed in the consolidation recorded below. *OT/DA theory* — Ben-David et al. [1]; Redko et al. [2]; Alvarez-Melis & Fusi [9]; Germain et al. [15]; Zhao et al. [16]; Mansour et al. [20]; Bonneel et al. [22]. *Flatness/PAC-Bayes* — Hochreiter & Schmidhuber [21]; Foret et al. [3]; Jiang et al. [4]; Ansuini et al. [5]. *Fine-tuning and optimisation* — Bottou et al. [6]; Cohen et al. [7]; Shimodaira [8]; Kumar et al. [18]; Wortsman et al. [19]; Howard & Ruder [41]; He et al. [26]; Pang et al. [27]; Berthier [28]. *DA-detection and flatness domain generalisation* — Cha et al. [17]; Zhou et al. [23]. *Measurement and reproducibility* — Guo et al. [14]; Xiong et al. [29]; Hangyu [30]; Yao et al. [31]; Abeykoon et al. [32]. The detector, corpus and few-shot anchors — [10]–[13], [24], [25] and [33]–[40] — are corpus and method anchors rather than theory or measurement anchors and are not classed here; their per-entry status markers, where present, are in the list itself.

**Reference identifiers and entries: corrections made in this version.** Every arXiv identifier in the list was re-checked entry by entry against OpenAlex, Crossref/DOI records and the arXiv abstract pages; seven were wrong at the time of that pass. Six of the seven entries concerned were merged into cluster citations or removed in the consolidation described below, so those identifier corrections no longer have an object and are not carried forward. The seventh is retained: the entry named "Large learning rates improve generalization, but hurt calibration" is not recoverable from OpenAlex or Semantic Scholar by title, and the identifier attached to it belongs to a different paper. It has been replaced by a verifiable calibration anchor — the present [14] — and the sentence in the manuscript that rested on the old entry was rewritten to state what the new reference actually shows. Two further entry-level corrections recorded by that pass, an author attribution and an author initial, concerned entries that the consolidation removed and likewise have no object. The verification and rewrite scripts are released with this manuscript. Which entry anchors what is recorded by the five anchor classes above.

**Status convention, stated for the ledger as a whole.** `[verified]` = volume/issue/pages or DOI re-checked against OpenAlex; `[preprint]` = arXiv only. Every entry that earlier versions of this ledger recorded as untraced, retired or replaced has been dealt with in the consolidation: the retired placeholder slot is gone from the list, and the entry no source could resolve is replaced by the verifiable calibration anchor [14]. All 74 entries carry a status marker — 31 `[verified]` and 43 `[preprint]` — so none is left un-rechecked; no unresolved placeholder marker remains.

# Appendix N. The two modules transferred from the companion paper: detail and provenance (2026-09-21)

> **Why this appendix exists.** The pre-registered multi-target replication (§8.7) and the three-way
> split and checkpoint-selection audit (§8.6) were developed as modules of the companion paper on
> evaluation validity and have been **transferred to this paper, which reports them first**. The main
> text carries their results; this appendix carries the module-level detail and the provenance that
> makes every value in them checkable, so that nothing in this paper rests on material the reader
> does not have.

## N.1 The registered replication: registration, criterion and archive

**The registration is prior to every run and this is checkable, not asserted.** The protocol was
frozen at **2026-09-13 01:37:27 UTC**, at which time the run directory did not exist, so the
criterion could not have been chosen after seeing a result. The registration document is
`预注册_新目标域复制实验_冻结_20260913.md` (11,611 bytes, md5 `9b09a573718546b62fea41b31935a05b`);
the file itself records a **content hash of `6a7eee7b3e34b15ce5adcba14cf7ea36`** for the text above its signature line. That value **is reproducible, and we state the convention it is computed over**: the span is the text above the signature line and the convention is LF-normalised, joined with LF, with a single trailing LF, which yields **7,175 bytes** for the hashed span; the search was by exhaustive enumeration over start point, end point, trailing newline and line-ending convention, and only the two equivalent solutions (first 76 lines plus a trailing LF, equivalently the first 77 lines with no trailing LF) reproduce the recorded digest. **The full-file md5 `9b09a573718546b62fea41b31935a05b` and the byte count 11,611 do match** the values recorded in this submission, and the freeze timestamp (2026-09-13 01:37:27 UTC) and the absence of any run directory at that time are recorded independently; what cannot be independently checked is the inner hash, and we say so rather than asserting a match.

**What the registration fixes, quoted rather than paraphrased.** Three unsaturated target domains; a
20% label budget; YOLOv12n with the shape-IoU loss; and a criterion of **≥2/3 pairs meeting all three of conventional significance (p < 0.01), at least eight of
ten seeds in the same direction, and an effect size of ≥+0.30 pp**, under a
Benjamini–Hochberg correction at **q = 0.05**. The archive holds **71 runs in total** — three pairs ×
2 arms × 10 seeds, a saturated control of 2 × 5, and one near-matched control appended by
amendment; **the earlier count of 90 did not follow from its own arithmetic and is corrected
here, the discrepancy being recorded in the audit trail as in §8.7.** **All 71 are re-keyed to the checkpoint each run itself recorded** — no run is
re-keyed to a checkpoint chosen afterwards.

**The three pairs, as registered and as read.**

| pair | registered | Δ (pp) | paired t | p | seeds positive | verdict |
|---|---|---|---|---|---|---|
| T1-a | `dota15→aitod` | +0.147 | 1.816 | 0.1027 | 6/10 | **fails** |
| T1-b | `aitod→visdrone` | +0.168 | 4.455 | 0.0016 | 10/10 | significance and direction met; **fails the +0.30 pp magnitude** |
| T1-c | `visdrone→dota15` | +3.727 | 43.774 | 8.5×10⁻¹² | 10/10 | **meets all three parts** |

**Reading the outcome.** After the correction **two of the three pairs survive at q = 0.05**; on the
complete three-part criterion **one of three** meets it. Across the pairs the effects move in the
same direction, with a mean of **+1.347 pp over the registered seed-pairs** (the mean of the three pair means: +0.147, +0.168 and +3.727), spanning **−0.22 to +4.32 pp**. The
outcome is therefore written **"criterion not met"** and not "hypothesis rejected": the registered
direction is stable across all three targets while the registered magnitude is met on one, and that
tension is the reported result rather than a defect in it.

**The limitation of the batch, stated with it.** It ran under the protocol in force at registration,
in which `val` and `test` coincide for the cells it measures, so **it is not a clean-protocol
result**: the level at which a checkpoint is read cannot be separated from the checkpoint that
selected it. The three-way work of §N.2 is a different batch and does not repair this one
retroactively. The honest reading of the registered set is evidence about **direction on three
targets**, not about magnitude on any held-out target.

## N.4 The domain-shift measurement behind the 2×2 design of §5

**What it is for.** §5 reports a within-pair budget manipulation on two domain-difference
tiers and states the measured shift of each tier (**D = 1.66** for the matched-corpus pair,
**D = 5.37** for the cross-corpus pair, s-OTDD). This appendix gives the measurement those two
numbers come from, so that they are not carried on assertion alone.

**The instrument.** s-OTDD, reusing the released shift codebase (`shift_families.py`) rather than
a re-implementation. Protocol points, all fixed before the measurement: ResNet-18 features at
512 dimensions; images resized to 224 with ImageNet normalisation; **cap 4,000** samples per side;
deterministically sorted, first $N$ taken; sliced Wasserstein-2 with `n_slices = 200`, `seed = 42`;
and s-OTDD taken as $\sqrt{W_2^2 + \text{label term}}$. $N = 282$ paired for the two tiers of the
2×2; the same-corpus reference row uses $N = 2{,}243$.

**The measured values, decomposed.** So that a reader can check the composition rather than only
the total:

| pair | tier | $N$ | feature $W_1$ | feature $W_2$ | label term | **D (s-OTDD)** |
|---|---|---:|---:|---:|---:|---:|
| `dota15_tr → dota15_te` | **A0, near-zero** | 282 | 0.0854 | 0.1149 | 2.7405 | **1.6594** |
| `dota15_tr → aitod_tr` | **A1, high** | 282 | 0.2380 | 0.2867 | 28.7135 | **5.3662** |
| *reference* `aitod_tr → aitod_te` | — | 2,243 | 0.0570 | 0.0740 | 1.6069 | **1.2698** |

The two tiers are separated by ≈ 3.2×, and both same-corpus values (1.66 and 1.27) sit well
below the cross-corpus 5.37, so the separation is not an artefact of the tier construction.

**The positive control, and why it matters here.** The same pipeline re-derived two **already
published** shift values and reproduced each to **Δ = 0.0000** (`shwd → sfchd_pool` = 11.2658;
`pcb → neu` = 23.2931). A pipeline that cannot reproduce values it did not originate is not
evidence about new ones, so this control is the licence for reading the table above.

**Where the numbers live.** The full measurement record — instrument, the same decomposition,
the control values and their reproduction — is `deliver/G1_D实测报告_20261004.md` in this
release; the measurement script is `code/g1_measure_D.py`. Two instruments for shift are used in
this paper (**N.3** states the separation): the one here, and the one behind §4.6's correlation
table (M.1). **They are not interchangeable and are never mixed within one comparison.**


## N.2 The three-way split and the checkpoint-selection audit: the per-run detail

**The split.** Each run's target corpus is divided into three disjoint parts — **33.31 / 29.74 /
29.86 mAP50-95** — with train, validation carve-out and held-out test sharing **no file name**, and the
reported value taken on the part no selection could see.

**Re-keying changes nothing, and that is the measurement.** Re-keying every run from its
training-time selection rule to this carve-out rule moves the within-domain mean by
**−0.069 pp** (t = −0.23, **p = 0.825**, 95% CI −0.758 to +0.620 pp) — a null, printed as a null.
**806 evaluations over 41 runs** enter this audit, of which **202 points are shared with an
independently archived evaluation and agree to the digit**; that overlap is the positive control
for the sweep.

**The premium, decomposed.** Hindsight capturable by selection is **0.7039 pp**. A rule taking the
current maximum captures **0.2114 pp = 30.0%** of it; averaging the top five epochs raises the
captured share to **69.6%** (0.4898 pp) at a selection-side cost of 0.7267 pp. Most of the premium
is a **shape** effect rather than a mislabelled one — on the selection side shape accounts for
**54.5%** of it — which is why the endpoint rule, not the difficulty of the split, is what the
reported level is sensitive to.

**Scope of this module.** The audit measures the *endpoint rule's* contribution on this pipeline. It
does not estimate the premium for any other pipeline, and the 0.077 pp difference between this
paper's two readings for `visdrone→dota15` (§8.7) conflates run-level reproducibility with the
endpoint-rule difference and is **attributed to neither**.

## N.3 Provenance of the transferred material

**The domain-shift instrument was recomputed rather than quoted.** The sliced-OTDD readings behind
the shift-comparison statement were recomputed on this submission's own pipeline, with a positive
control: reproducing the published within-domain cell (`MAFA→mask`) is recovered at **7.1894**,
matching the published value exactly. The cross-domain values computed for this submission are
`visdrone↔dota15` **8.0226**, `aitod↔visdrone` **8.7739**, `dota15↔aitod` **5.1726**,
`dota↔dota15` **0.7386** (its Wasserstein term identically zero), `dota↔aitod` **5.1627** and
`dota↔visdrone` **8.0162**. **The published within-domain values are cited as published and are not
recomputed or replaced here**, because this pipeline's within-domain readings do not reproduce them
(for `VisDrone` it returns 3.2799 against a published 6.4273), so the instrument is used only where
the positive control licenses it. The two readings are reported as measuring different constructions
and are not merged.

**Every artifact retrieved for this submission, with its hash.**

| artifact | bytes | md5 | role |
|---|---|---|---|
| `sotdd_aerial.csv` | 787 | `cf54319487f3362e8c85382c31fa6b9d` | the recomputed s-OTDD readings of §N.3 |
| `sOTDD_aerial.py` | 5,364 | `e4ef65638c5500c8eb705fe2cea8bc96` | the script that computes them |
| `extract_dota_feats.py` | 5,133 | `3f2081c6841e93c0bc5d0d0586e18fd3` | feature extraction, with a bit-identical self-check |
| `extract_dota.log` | 699 | `19fe468088da5c87354b7d831453d405` | the extraction log the self-check is read from |
| `r10_p_vistod15_base100_3way_s42n_args.yaml` | 1,801 | `2e77971c8f5244c497a5fe4e286c9cf9` | the recorded configuration of the third cell (`visdrone_pretrain.pt` + `dota15_20p_3way.yaml`); ★ **this one file is not part of the released set** — its recorded size and digest are given here so that the reading can be checked against a copy if one is available, but we do not ship it |

**Environment and settings, to the limit of what was recorded.** The recomputation ran on a separately
and the frozen log of that run preserves the settings but **not the library version
strings**: the interpreter and package versions were not written into the log, so this submission
does not state them. What is recorded, and is what the numbers depend on, is that all s-OTDD runs
used ResNet-18 `IMAGENET1K_V1`, 512-dimensional features, 224² inputs, **200 slices**, `seed = 42`,
equal weights over the two label terms, and truncation at `n = min(n₁, n₂)`. **This is the
published-table convention, adopted unchanged**, so that the instrument is comparable with the
published table rather than a new one. The extraction step carries its own self-check: re-deriving
the cached `dota15_tr` features under the same parameters gave a maximum absolute difference of
`0.000e+00` with label agreement `True`, i.e. **bit-identical**, which is what licenses reading the
new corpora through the same instrument.

**What the transfer does and does not carry.** The two modules are this paper's from this version
onward and are reported here first; the companion paper retains its own independent readings for the
one cell the two share, and **neither paper describes that cell as a cross-implementation
replication** — the fingerprint comparison shows one recipe, one training set, one implementation
and one seed set run twice. The companion paper's deprecation of its own §8 means its
`可引用材料` framing for these modules is withdrawn; the underlying released runs remain the
checkable record.


# Process protocols shared with the companion paper (internal tools; declared, not attached)

> **Purpose.** §9.2 reports that the dead-layer duplication was caught by the blinded external audit pass and that the
> pass is advisory. That pass, and the working method behind the scripted campaign,
> are **project-internal protocols shared with the companion paper** (the evaluation-validity paper):
> both papers use the same protocols and **neither presents them as a contribution of its own**.
> Following the same form the companion paper's supplementary material uses (its §S6), the declaration
> is given as **file name + md5, with no text attached** — these are internal working documents, not
> publications, they contain no unpublished results, and nothing in this paper's reproduction path
> depends on them. They can be supplied with a revision on request. The third row is the
> internal change-log referred to by the audit-anchor paragraph below; it is declared in the same
> form, for the same reason.

| Internal document | md5 | Role in this paper | Claimed as original? |
|---|---|---|---|
| `多模型盲审清单_通用_20260915.md` | `e4c73a5ca5992b7af6a5a66c84ba4561` | the blinded external audit pass of §9.2 — the layer that caught the dead-layer duplication | **No** — shared; claimed by neither paper |
| `DSH+本地+云端_工作方法指南.md` | `10d1b3a3e21f018f3b82e4a293242695` | scripted local/cloud execution, all-or-nothing patching, the audit-anchor discipline and the per-number local-pointer rule | **No** — shared; claimed by neither paper |
| `内部_压缩记录_20260918.md` | `AC9A0C159874616FF9DA81C7EEFC04D9` | the compression record: the verbatim ledger of what the length-reduction passes removed from the main text, kept as a working record of the audit trail (§9.2, Appendix E). **34 of this paper's audit anchors check this log's own provenance bookkeeping** — its own internal consistency and the historical citation indices it preserves — and **no reported result, number or claim depends on it** | **No** — internal bookkeeping; not a source of any claim. Its md5 changes whenever its own header is amended, and the value above is the current one |

**The audit-anchor system falls under the same convention.** This paper's **529 anchors over the submitted material**, and a further **36** that check the internal change-log declared above — the log is an internal document retained outside this submission and is **declared rather than attached** (file name and md5 in the table above; available on request), and **no reported result, number or claim depends on it**. The companion paper's anchors and these are *one shared instrument*. Neither paper presents the anchor system, the six-model review protocol, or the working method as its own methodological contribution; each cites them as process.


---

**Note on the compression record.** Earlier versions of this file ended with a "compression record" that reproduced, verbatim, the material removed from the main text by the length-reduction passes. That record is **not part of this submission**: it is maintained as a separate internal document, because it is a working ledger rather than supplementary scientific material, and because its citation indices are those of the pre-consolidation reference list. Everything the record preserved that bears on the paper's claims is printed in the live text and appendices above; the released runs, tables and scripts named there remain the checkable record.

**Data and code availability.** The released readouts, the three-way split construction and the analysis scripts that produce every number in this paper are archived at https://github.com/YBP2005/Cross-Domain-YOLOv12 (commit reproducibility-package-v1), together with a manifest of file hashes and a table mapping each reported number to the file and rows it comes from. The trained checkpoints, and the per-seed file of the B-pipeline published-protocol readings, are available from the corresponding author on reasonable request.

# Appendix O. Related-work detail removed from the main text (2026-10-02)

> **Why this appendix exists.** Two families of prior work are cited in the main text in compressed form, so that
> the article's §2 and §6 carry the positioning without carrying the enumeration. The per-paper differences are
> recorded here, with the verbatim overlap in each case. Every entry was read at **abstract level** through the
> channels recorded in §O.3; **none was read as a full text**, and no entry here should be read as "no work exists
> that does X" — see the channel statement below.

## O.1 The first-order-geometry family, paper by paper (cited from §6)

| Work | Verbatim overlap | Overlap | Difference in layer |
|---|---|---|---|
| **Andriushchenko, Croce, Müller, Hein**, *A Modern Look at the Relationship between Sharpness and Generalization*, ICML 2023 (arXiv:2302.07011) | *"sharpness does not correlate well with generalization but rather with some training parameters like the learning rate"*; *"a consistent negative correlation of sharpness with out-of-distribution error"*; *"the right sharpness measure is highly data-dependent"* — its setting includes fine-tuning CLIP and BERT | **substantial** (conclusion, premise, genre) | they **question the correlation**; we fix a **pre-registered SNR gate** per cell and report the resulting **signs**, and add one sign flip produced by the reporting column alone |
| **Dziugaite et al.**, *In Search of Robust Measures of Generalization*, NeurIPS 2020 (arXiv:2010.11924) | meta-evaluation: unreliable measures *"can obscure failures and successes"* | substantial (meta-evaluation stance) | same stance; different instrument |
| **Dinh, Pascanu, Bengio, Veness**, *Sharp Minima Can Generalize For Deep Nets*, ICML 2017 (arXiv:1703.04933) | flatness/sharpness reads are **not invariant to reparametrization** | partial (premise) | we do not re-argue invariance; we measure a **noise floor** |
| **Kwon et al.**, *ASAM*, ICML 2021 (arXiv:2102.11600) | adaptive sharpness fixes scale-invariance but *does it capture generalization in modern settings?* | partial (premise) | as above |
| **Jiang et al.**, *Fantastic Generalization Measures*, ICLR 2020 (arXiv:1912.02178) | the measure family itself | partial (measure layer) | as above |
| **Musgrave, Belongie, Lim**, ECCV 2020 (arXiv:2003.08505) | metric-learning evaluation caveats | partial (measure layer) | as above |
| **Dodge et al.**, EMNLP 2019 (arXiv:1909.03004); Dodge et al. 2020 (arXiv:2002.06305) | **checkpoint-selection** changes reported conclusions | **closest to (b)** | they vary the *selection* rule across runs; we hold runs and seeds fixed and vary **only the reported column** on **one** cell |

**What remains ours in §6** (and is *not* in any of the above): ① the **gate fixed before the data existed**, applied
per cell, failing on **18/18**; ② the **ε-scaling exponent 0.56–0.81** read as a *mechanism* (first-order dominated at
the customary radii) rather than as another correlation; ③ the single-cell sign flip produced by **the reporting
column alone** (+0.628 pp on the held-out test column vs −0.307 pp on the validation-selected best-checkpoint column).

## O.2 The budget / scaling-law family, paper by paper (cited from §2)

All of these are statements about **where the optimum sits** (or how it moves) under a budget change — the layer the
main text says is *known*. They differ from this paper in that none reports a **paired gain** whose **sign** is read
under a budget intervention on the fine-tuning axis.

| Work | Verbatim overlap | Axis | Why it is not this measurement |
|---|---|---|---|
| **Bjorck et al.**, *Scaling Optimal LR Across Token Horizons*, ICLR 2025 (arXiv:2409.19913) | *"the optimal LR changes significantly with token horizon — longer training necessitates smaller LR"* | pretraining tokens | a law for the **optimum's location**; no paired gain, no sign |
| **Li et al.**, *Rethinking the Hyperparameters for Fine-tuning*, ICLR 2020 (arXiv:2002.11770) | *"the effective learning rate … sensitive to the similarity between the source domain and target domain"* | source–target similarity | as above |
| **Mosbach, Andriushchenko, Klakow**, *On the Stability of Fine-tuning BERT*, ICLR 2021 (arXiv:2006.04884) | *"the role of training dataset size per se is orthogonal to fine-tuning stability. What is crucial is rather the number of training iterations"* | iterations (NLP) | mechanism-side support for the **epoch** axis; not detection, not paired, not a sign |
| **Li et al.**, 2026 (arXiv:2602.06797); **Sakai & Imaizumi**, 2026 (arXiv:2609.35029); **Shulgin et al.**, 2026 (arXiv:2603.15958); **Bu et al.**, ICLR 2026 (arXiv:2602.07145); **Ajroldi et al.**, 2026 (arXiv:2608.28308); **Rehn et al.**, 2025 (arXiv:2510.20616) | closed-form schedules / phase transitions / transfer conditions under a fixed horizon; *"both undertraining and overtraining regimes"*; *"the existing heuristics for tuning B do not work"* under a fixed compute budget | various (LLM, DP) | all fit or bound an **optimum**; none reports a paired-gain sign on a detector |
| **Hernandez, Kaplan, Henighan, McCandlish**, *Scaling Laws for Transfer*, 2021 (arXiv:2102.01293) | *"the effective data transferred is described well in the low data regime by a power-law of parameter count and fine-tuning dataset size"* | **data** budget | a power law with **no sign change and no bound** |
| **Springer et al.**, 2025 (arXiv:2503.19206) and **Everett & Qiu**, 2026 (arXiv:2609.04577) | *"extended pre-training can make models harder to fine-tune"*; *"the preferred learning rate schedule can reverse across the overtraining axis"* | **pretraining** budget | these **do** report a reversal — but on the pretraining axis and on optimizer preference, not on a paired fine-tuning gain |
| **Zhang, Xu & Agrawal**, 2026 (arXiv:2606.30795) | *"several variants switch from positive gains at 1% to neutral or negative effects at larger budgets"*; *"leaving less room for noisier and less stable interventions"* | **labelled target budget**, detection | the closest work; the difference is one of **role and criterion** (see §4.6 of the main text) |
| **Pardo et al.**, *BAOD: Budget-Aware Object Detection*, CVPRW 2019 (arXiv:1904.05443) | budget as a **constraint the algorithm optimises under** | compute | the opposite role to ours |

## O.3 Channel statement for this appendix

Every entry above was reached through a jump host and read at **abstract level only**. The appendices of this paper record **two rounds** of search, and the channel state differed between them, so we state both rather than one.

**First round.** During the positioning check that produced the tables above, **`export.arxiv.org/api/query` returned HTTP 429 throughout** (empty responses, which are **fetch failures, not zero hits** — confirmed with a known-absent control term), **OpenAlex exhausted its daily budget**, Semantic Scholar returned 429, and **no Chinese-language index was reachable**. Three of the eight claims of the novelty review were consequently left at low evidence strength (the same-domain reading, the isolated backbone swap, and the annotation-density moderator).

**Second round (re-run for those three claims).** A later session re-ran them on a restored channel: **Crossref, DataCite, the arXiv API, the arXiv landing pages and OpenAlex all answered**, and the arXiv API produced well-formed responses. Two properties of these channels were measured and are recorded because they change how a negative may be read:

* **A zero-hit arXiv response is 700–800 bytes** (the absent-term control returns 728 bytes) whereas a response with hits is several thousand; and an HTTP 429 with a one-byte body is a **throttled fetch**, not a zero-hit. The three are distinguishable only by reading the status code and the length together, and we report the throttled fetches as failures rather than as absences.
* The arXiv API's **quoted-phrase** queries (`abs:"…"`, `all:"…"`) return HTTP 200 with 14–23 kB of **unrelated recent submissions** rather than matches; only unquoted multi-word conjunctions were used as evidence. Semantic Scholar (no key) and the dblp API (bot challenge) remained **unusable** in the second round, and those two are the highest-coverage channels for detection preprints.

**What the re-run changed, and what it did not.** It returned same-layer prior work that the first round had not reached: label statistics used to predict transfer difficulty without training a model [35], source-model accuracy used to predict transfer [36], isolated backbone comparison inside detection [37][38], and the separation of architecture from pretrained weights [39]. The main text cites all five and scopes its claims accordingly (§2, §4.4, §4.6, §9). It did **not** return, in either round, a paired-gain measurement of the kind this paper reports, nor a significance test on the **difference** between two backbones' budget gains, nor an annotation-density moderator of the **sign** of a gain.

Consequently the tables above are statements about **what was found in the channels reachable at the time**, and the absence of an entry is **not** evidence that no such work exists. This is a statement about coverage, not a licence: a reader who knows of work in the two unusable channels should read these sections as incomplete.


# Appendix P. The resolution criterion, the size rule, and bounded nulls (2026-10-04)

> **Why this appendix exists.** §9 states the study's resolution audit in one criterion and §4.2 separates an observed
> range from an inference bound. Both are computations over the released per-cell table
> (`theory_B_MDE_by_cell.csv`, 147 rows, regenerated by `scripts/43_A24_power_audit.py`), and both were
> compressed in the article so that the article carries the judgement rather than the arithmetic. This appendix
> carries the arithmetic, and it is **not** counted against the article's page limit.

## P.1 One criterion behind the audit and the MDE

**On citation form in this appendix.** The references introduced by these *Prior work* notes are cited here **by author and identifier** (arXiv number or DOI) rather than by bracketed number, because this appendix carries its own historical numbering ledger that is not interchangeable with the article's reference list; see the reference-status note below. The article's list is unchanged.

**Prior work.** The use of a minimum detectable effect as a *gate on model-evaluation claims* is not introduced here: Arviv et al. (arXiv:2607.08522, 2026) make the statistical power needed to rank, select and test a model an explicit prerequisite of an evaluation stopping rule, and Zhuang, Li and Fan (arXiv:2605.28873, 2026) derive a **paired** MDE budget and phrase their audit as the observed deltas falling below the implied MDE. What this appendix supplies is not the criterion but the **inventory**: the criterion applied cell by cell to a released archive, with the resulting counts.

For a paired design with $n$ seeds and per-seed differences $D_i$, let $\hat\sigma$ be their sample standard
deviation and let

$$\gamma(n)\;:=\;\frac{t_{1-\alpha/2,\,n-1}+t_{1-\beta,\,n-1}}{\sqrt n},\qquad \alpha=0.05,\ \beta=0.20 .$$

Then the minimum detectable difference is $\mathrm{MDE}(n,\hat\sigma)=\gamma(n)\hat\sigma$, and a cell is
**resolvable** exactly when $|\bar D|/\hat\sigma\ge\gamma(n)$. The right-hand side is a function of $n$ alone, and
the left-hand side is a sample-size-free standardised effect; the audit's threshold and the MDE of §4.2 are
therefore the same object evaluated at two sample sizes.

| $n$ | 3 | 5 | 8 | 9 | **10** | 13 | 20 |
|---|---|---|---|---|---|---|---|
| $\gamma(n)$ | 3.0965 | 1.6625 | 1.1528 | 1.0650 | **0.9947** | 0.8463 | 0.6605 |

Calibration: $n=10$, $\hat\sigma=0.3080$ pp gives $\mathrm{MDE}=0.3064$ pp, matching the article's
0.306 pp. The per-cell counts of §9 follow from this table applied row by row: **147** cells scored,
**43** with $|\bar D|<\mathrm{MDE}$, of which **32 of 73** at $n=3$ and **11 of 74** at $n>3$.

**The two seed counts, read correctly.** The median $|\bar D|/\hat\sigma$ is **4.37** among the $n=3$ cells and
**3.03** among the $n=10$ cells, so the two groups differ in **standardised effect** as well as in size, and the
44%-against-15% contrast is a description of two groups rather than evidence that more seeds resolve more. Re-basing
the $n=3$ cells to $n=10$ at their own $\hat\sigma$ leaves **23%** unresolvable against the **14%** actually observed
at $n=10$; the gap between those two percentages is the part of the contrast that is a selection effect rather than
an arithmetic one, and we report it as such rather than attributing the whole contrast to either cause.

## P.2 Why ten seeds, and why that is not an ex-ante rule

The registered magnitude bar is $+0.30$ pp ($\S3$; the bar is carried over from the frozen criterion of
`判据冻结_P1_v4_20260927.md` §1). At the archive's **median** $\hat\sigma=0.2744$ pp:

| $n$ | 8 | **9** | 10 | 11 |
|---|---|---|---|---|
| $\gamma(n)\hat\sigma$ | 0.3163 | **0.2922** | 0.2729 | 0.2571 |

so **$n=9$ is the smallest integer at which a 0.30 pp effect is resolvable at 80% power against the archive's
median noise**, and the ten-seed bar used throughout this paper sits **one seed above that minimum** rather than at it — which is the honest form of the statement, and it is also why the bar must not be read as having been derived from the noise. Two qualifications are part
of the statement. First, $\hat\sigma$ is known only after a cell has been run, so this is a **retrospective account
of the size chosen, not an ex-ante rule**; a pre-run rule would need a pilot $\hat\sigma$ named at registration.
Second, the components of $\hat\sigma$ available here are the **data-order** components, with the augmentation
component (0.246 pp on the strategy arm) excluded by the registered design (§F.1), so $\hat\sigma$ is a **lower
bound on the noise** and the bars built on it are **looser** than their nominal level; the $n=3$ estimate of
$\hat\sigma$ in particular has a CI of $[0.5\times,6.3\times]$ (§F).

## P.3 Bounded nulls, and the standard they meet

A **bounded null** for a modulation contrast is the statement $|\bar D|\pm \mathrm{HB}\subseteq(-b,b)$ with
$\mathrm{HB}=t_{1-\alpha/2,n-1}\hat\sigma/\sqrt n$ the half-width. §4.2's second row is the archive's clearest
case, and the two numbers it supports are different:

| quantity | value | what it is |
|---|---|---|
| observed spread of the four point estimates | **0.12 pp** | a description of this sweep (0.694 to 0.812) |
| 95% half-width at $n=10$, $\hat\sigma=0.321$ pp | **±0.23 pp** | the inference bound this row can carry |
| 80%-power MDE of the 30-versus-200 endpoint difference | **0.306 pp** | a different statistic: a *contrast*, $\hat\sigma=0.308$ pp |

**Only two of the 45 paired epoch-axis differences reach an MDE of 0.31 pp or below**: the cell above, and a
same-domain cell (`dota15→dota15`, 100→200 epochs, $-$0.066 pp at MDE 0.229 pp). A bounded null at this standard is
therefore a result this design produced at one cross-domain cell, not a claim available archive-wide.

## P.4 What this appendix does not claim

It does not calibrate the bars: the noise scale is a lower bound (§P.2) and the thresholds are therefore looser than
nominal. It does not make the size rule prospective: the rule in §P.2 is retrospective. And it does not extend the
audit to the differenced readings, which have their own statistics and are not in the released table.

## P.5 Scope of the two instruments, and the audit's own limits

The article uses two screening instruments, and they answer different questions. The **seed gate** (§4.5) asks
whether a **sign is stable across seeds** — a difference enters the counts only if it rests on ten paired seeds, or
on at least five with a unanimous sign, or reaches $|t|\ge4$. The **resolution audit** (§9) asks whether a
**single-budget level** is distinguishable from zero at 80% power. Neither implies the other, and both are
**filters or descriptions rather than tests**: neither carries a nominal error rate, and the family-level
Benjamini–Hochberg correction is reported as robustness only, because the roster of cells was enumerated after its
outcomes were seen. A cell may pass the gate and fail the audit; the gate's eligibility is then unaffected and only
the reading of that cell's **magnitude** is withdrawn.

Three further limits belong to the audit and are stated here rather than in the article:

1. **It covers levels, not contrasts.** Every conclusion of §4 is stated on a **difference** between two budgets or
   two backbones, and a difference has its own paired statistic and its own MDE, neither of which is in the released
   per-cell table. §4.2 quotes one such number explicitly (SD of the per-seed endpoint differences 0.308 pp, hence
   MDE 0.306 pp). The audit's verdicts are not transferred to the differenced readings.
2. **Its roster is a census.** The 147 rows are every cell on the `test_map50_95` column with at least three paired
   seeds: no analysable cell is missing and no row falls outside that definition (recomputed and checked by
   `scripts/43_A24_power_audit.py`). Because each row is an independent per-cell decision, the audit needs no
   multiplicity correction of its own; because the roster was assembled after outcomes were known, the audit is
   nonetheless a **description of this archive** and not a pre-registered family.
3. **Its threshold is uncalibrated.** The noise scale it divides by is a **lower bound** on the total noise (§P.2),
   so the audit flags **fewer** cells than a fully calibrated threshold would, and "resolvable" as used here means
   resolvable against the noise components this design measured.

## P.6 The held-out sign prediction of §4.5, family by family

The article reports the exercise in one paragraph; this table carries the per-family detail so that the 21-of-25
figure can be audited and so that the failures are visible individually rather than as a residual.

**Method.** For every `(pair, family)` with readings at two or more epoch budgets, the epoch-axis endpoint
difference is computed within each **label budget** slice (earliest to latest epoch available, paired on the shared
seeds, `test_map50_95`). The **lowest label budget** of each family fixes the predicted sign; every **higher** label
budget is held out and scored against it. The split is fixed by budget order and not by outcomes. The companion
exercise holds out the epoch budget instead: for each `(pair, family)` with readings at two epoch budgets, the
label-axis endpoint difference measured at 30 epochs predicts the sign at 100 epochs.

**Result.** 21 of 25 held-out slices correct; 4 of the 6 families carrying all five label budgets unanimous;
7 of 7 families correct on the cross-epoch label-axis exercise. The independent units are the **families** (seven),
not the slices.

| pair / family | label budgets used | sign fixed at lowest slice | **held-out slices** | **predicted correct** | verdict |
|---|---|---|---:|---:|---|
| `pcb→neu_det` / `s2df` | 10/20/30/40/50 | negative | 4 | **4** | all five same sign |
| `chv→gdut_hwd` / `s2hv` | 10/20/30/40/50 | negative | 4 | **4** | all five same sign |
| `fsin→smoke_keremberke` / `s2sm` | 10/20/30/40/50 | positive | 4 | **4** | all five same sign |
| `visdrone→dota15` / `s2ae` | 10/20/30/40/50 | negative | 4 | **4** | all five same sign |
| `mafa→mask_clean` / `s2mk` | 10/20/30/40/50 | `+0.057` at 10% | 4 | 3 | fails at 30% (`−0.547`) |
| `shwd→sfchd` / `a0` | 10/20/30/40/50 | `−0.200` at 10% | 4 | 2 | fails at 40% (`+0.233`) and 50% (`+0.327`) |
| `shwd2sf→sfchd` / `a0` | 20/40 | `−0.320` at 20% | 1 | 0 | fails at 40% (`+0.097`) |
| **total** | — | — | **25** | **21** | — |

**Falsification condition, and its current status.** The exercise is refuted in a family whose two label-budget
slices carry endpoint differences of **opposite sign that are each separately resolvable** ($|d|$ at least its own
MDE). **None** of the failures above meets that description: each sign-reversing pair has at least one slice whose
endpoint difference falls below its own 80%-power minimum detectable difference under the $\gamma(n)$
convention of Appendix P, and the shortfalls are large (on `mafa→mask_clean` the 10% slice is off by a factor of about 75
and its 30% slice by about 8). The falsification condition is therefore **not yet instantiated on this archive**; what the
failures establish is the weaker statement that the sign is not unanimous within a family, which is why the
result is stated as "four of the six families that carry all five label budgets unanimous, with named
sign-reversing exceptions" — not "the sign is a property of the pair".

**One limitation of the test itself.** The test was decided after the archive existed. Its split is prior (budget
order, outcome-blind), but its existence is not, and we record that distinction rather than claiming a
pre-registered prediction.

## P.7 The saturated control, per batch and per column

§4.3 reports a damage on one column and its independent batch on the same column. This table carries the four
numbers so that the column dependence can be audited rather than taken on trust.

| batch | family | label budget | epochs | `test_map50_95` (held-out test) | `best_map50_95` (validation-selected) |
|---|---|---|---|---|---|
| first | `t2` | 20% | 100 | −1.156 pp (t = −3.03, n = 10) | **−1.428 pp (t = −6.69, n = 10)** |
| second | `r10` | 20% | 100 | **−1.170 pp (t = −3.39, n = 13)** | +0.004 pp (t = +0.02, n = 13) |

**How to read it.** §4.3 declares the validation-selected column, and on that column the first batch supplies the
damage while the second supplies a **null**. The two batches agree only on the held-out test column. Neither column
is wrong; they answer different questions, and the article's §3 convention assigns the val-best column to §4.3 and
§4.4 while §4.1–§4.2 use the test column. The same column dependence is what §6(b) reports for the primary pair,
where one cell reads **+0.628 pp** on the test column and **−0.307 pp** on the val-best column with runs, seeds and
fine-tuning untouched. The consequence stated in the article is that the saturated-target damage is **carried by one
batch on one column**, and that the independent batch supports it only on the other column.

## P.8 Resolvability as a function of the reporting column

**Prior work.** That checkpoint selection on a validation criterion can bias the reported test reading, and that the direction of that bias can differ between criteria, is already established: Varma and Simon (DOI:10.1186/1471-2105-7-91, 2006) for selection inside cross-validation, Forstmeier and Schielzeth (DOI:10.1007/s00265-010-1038-5, 2010) for the direction of the optimism, and Suo, Wang and Li (arXiv:2607.27655, 2026) and Apicella et al. (arXiv:2602.22107, 2026) for checkpoint selection and validation criteria specifically. This appendix therefore claims no discovery of the bias. Its increment is narrower and countable: the cell set is fixed by `(pair, family, label budget, epoch budget)` over cells whose dataset name carries an **explicit label budget** (the derived field must be non-null, which excludes the `r10`-family cells whose names have no budget suffix); the disagreement between two columns is resolved **against each cell's own MDE**, and the eleven disagreeing cells are then decomposed **exhaustively** into the point-estimate channel and the variance channel.

**What this appendix adds.** The main text states that switching between the two readout
columns changes a cell's resolvable / unresolvable verdict. This appendix gives the count, the
per-cell composition, the robustness checks and the limits, so that the claim can be recomputed
from the released per-run tables rather than taken on assertion.

**The object, stated so it can be recomputed.** For a cell $c=(\text{pair},\text{family},
\text{budget},\text{epochs})$ we take the per-seed paired gain
$d_s = 100\,[\text{lr005}_s-\text{base}_s]$ in percentage points, its mean $\bar\Delta$, its
sample SD $\hat\sigma_d$ over the common seeds, and the same 80%-power minimum detectable
difference used by the audit of §9 and Appendix P.1,
$\mathrm{MDE} = (t_{1-\alpha/2,\,n-1}+t_{1-\beta,\,n-1})\,\hat\sigma_d/\sqrt n$ with
$\alpha=0.05$, $\beta=0.20$. A cell is **resolvable** when $|\bar\Delta|\ge\mathrm{MDE}$.
The exercise is run once per column, on the cells where **both** columns are complete and the
common seed count is $n\ge 3$; no cell is ever formed by mixing the two columns.

**The count.**

| epoch budget | cells with both columns, $n\ge3$ | **verdict changes with the column** | share |
|---|---:|---:|---:|
| 30 | 45 | **5** | **11.1%** |
| 100 | 63 | **7** | **11.1%** |

Two features of the count matter. First, the **share is the same at both budgets (about 11%)
even though the two columns' mean gap is not**: the difference between the columns' cell gains,
$\bar\Delta_{\text{test}}-\bar\Delta_{\text{val-best}}$, is $-0.043$ pp at 30 epochs
($t=-0.46$, $p=0.65$) against $-0.482$ pp at 100 epochs ($t=-3.12$, $p=0.003$). The verdict
flip and the mean gap are therefore **two different statements** and are not combined here.
Second, of the seven 100-epoch cells, **five are verdicts that are unresolvable on the test
column and resolvable on the val-best column**; the remaining two move the other way.

**Reporting clusters, not independent experiments.** The seven 100-epoch cells fall in **four $(\text{pair},\text{family})$ clusters** — three of the seven share one pair and family, and slices
inside a family share their data source, pretraining and seed set. These clusters are **reporting
strata, not four independently validated target-domain replications**: the released run table
carries no image-membership manifest or sample-content hash, so neither the independence of the
clusters nor the absence of image-level overlap between them is established here. On the same convention used
elsewhere in this paper, the count of evidence is **four reporting strata**, and the appendix does not present
seven.

**Robustness.** Raising the minimum seed count from three to six moves the 100-epoch count only
from $7/63$ to $4/28$, i.e. the share rises from 11.1% to 14.3%; the pattern is therefore not an
artefact of the lowest-inclusion cells. At 30 epochs the 45 cells give 5 flips, so the phenomenon
is present at a short budget as well, and no reading across budgets is offered.

**Limits, stated with the result.** (i) The cells are **not matched across epoch budgets** — the
45 cells at 30 epochs and the 63 at 100 epochs are different (pair, family, budget) sets — so
nothing here is a monotone statement about the budget. (ii) The cluster count is
**four**, and it bounds how much weight the count can carry; it is a count of reporting strata,
not of independent experiments. (iii) The base table records a
*seed kind* per run, and in **20 of the 169 gated cells** the two arms' seed kinds are **not the
same set**; here "the same seed" is therefore a pairing asserted from the run records rather than
one verified independently, which is why the verdict change is reported as an observed property
of the two columns and is not attributed to a mechanism.

**Why it is checkable.** The released per-run tables carry both columns for every run, so a
reader can recompute both verdicts per cell without re-running anything. Where the two columns'
paired-difference spreads differ, the **same** $\bar\Delta$ crosses one column's threshold and
not the other's; that is the sense in which the verdict belongs to the convention.

## P.9 Boundaries of the released cell definition, and what they do not affect

The per-run tables are keyed on a cell defined as (pair, family, label budget, epoch budget).
Four properties of the released material bound how far a cell can be read. Each is reported
here because it constrains *interpretation* rather than the arithmetic: the numbers in the
tables are what the stated key produces, and none of the four changes any reported number.

**1. The cell key does not carry the box-regression loss prior.** `loss` is one of the axes
this paper varies, but it is not part of the key. Measured on the released table: in **40**
(cell, seed, arm) slots the same key holds runs with **more than one** `loss` value, and in
**40 of 40** of those slots the readings differ between the two losses. (The same phenomenon counted
per (cell, seed), pooling both arms, occurs in **20** slots; we use the per-arm count because that is
the unit the parser selects in.) Selection inside a
slot is deterministic but was, until this round, incidental: the released parser breaks ties
by run-name length, and the `shapeiou` records are the shortest, so it took `shapeiou` in every
observed case. That rule is now explicit in the parser (`shapeiou` preferred, then the outcome
rank, then name length), and the explicit rule reproduces the released cell values exactly:
**0 of 338 cells (both columns) change**. The boundary to carry forward is that a cell in this
release is a `shapeiou` cell, and a comparison across loss priors is not available at this key.

**2. The three-way-protocol flag is collinear with one family.** Of the **389** runs carrying
`threeway = 1`, **363 (93.3%)** sit in the family `r10` and the remaining 26 in `g4`. The flag
is therefore close to a family label in this archive, so any contrast drawn between the
clean three-way protocol and the published protocol is at the same time a contrast between
`r10` and the other families. This does not weaken the protocol argument, which rests on the
construction of the split rather than on a between-family contrast, but it does mean the two
readings are not separable here and should not be presented as if they were.

**3. A residual set of runs records a seed that its run name contradicts.** Those runs are named
with one seed but carry another in their configuration; they are excluded from every seed-gated
count in this paper, and no reported number rests on them. The residual is small and we do not
resolve it here.

**4. What fraction of the label axis is actually labelled.** The label budget is the measured
independent variable of §4 and §4.6, so how much of the archive carries a *checkable* budget
label is a bound on that axis. Of the **2,362** runs in the released table (the same base as §3), **453 (19.2%) carry no
parseable label budget**. **442 of those are recoverable to 20%** from configuration evidence —
a saved dataset YAML whose `train` path contains `20_percent`, or the generated split
specification together with its execution log. (The recovery itself is carried out on the analysis
table of 2,570 run-rows that the accompanying analysis package ships, a superset of the 2,362 runs
above; **266** of the recovered rows are usable for pairing there. The two row counts are different
objects and we do not mix them.) A further **13 rows** carried a parser artefact, in which a run name read as a budget
what was not one (`g1p` as 1%, `dose2p5x` as 2%); these are now left **unlabelled rather than
guessed**. The recovery does not change any cell count: the complete 5x2 label-by-epoch
rectangles remain **6**, the cells with both arms remain **168**, and the resolvability audit of
§9 is unaffected because it does not require a budget label. What the axis has, therefore, is a
documented coverage boundary rather than a complete label set.
 In **25** rows the
stored `seed_used` differs from the seed embedded in the run name; in every one of those rows
the stored value is `42` while the name carries a different seed, and every one is an
incomplete or restarted run (`_PARTIAL_*`, `_OOMKILLED_*`, `_oomfix`, `.incomplete_*`).
Consequently in **5** (cell, seed) slots the base and strategy arms do not share the same
embedded seed, so for those slots "the same seed" is a pairing asserted from the stored field
rather than one verified from the run names. Four of the five slots are residual runs and one
is a released cell, so the effect on reported values is small; the boundary is recorded because
the paired-by-seed convention is stated as a property of the whole archive.

**What follows from the three.** The released per-run table supports recomputation of every
reported number, and it does so under a key that is narrower than the design: loss prior is
fixed by selection rather than by the key, the protocol flag is confounded with a family, and a
small residual set carries a seed field that its name contradicts. A reader who needs a cell
that varies loss prior, or that separates protocol from family, will not find it in this
release, and we would rather state that than leave it to be inferred.
## P.10 Arm-level accounting for a falling budget gain

**Prior work and scope.** Writing a change in a difference as the difference of two arm-level changes is an identity, not a method, and prior work on budgeted training already reports individual instances of both catch-up and degradation. The claim here is a **census** over a released archive, not a new estimator, and $C$ and $A$ are measurements rather than mechanism.

A gain that falls as the epoch budget grows can be accounted for in two ways, and the two are
separable without any new run. Fix a (pair, family, label budget) triple and two epoch budgets
$l<h$; for every seed with all four runs present write $B_l,I_l,B_h,I_h$ for the two arms, and
define

$C=B_h-B_l$, $A=I_h-I_l$, $D=C-A$.

$C$ is the absolute movement of the baseline arm, $A$ that of the intervention arm, and $D$
equals the fall in the gain, $G_l-G_h$. **The identity is not a new statistical method**, and
prior work on budgeted training already reports individual instances of both catch-up and
degradation; what is reported here is what the released archive contains as a **census**, not a
new estimator. All quantities are in mAP50-95 points, intervals are conditional $t$ intervals on
the same-seed paired differences, the two columns are computed separately and never pooled, and
**every decomposition is taken inside a single family**: pairing across families would fold a
protocol difference into what is read as an epoch effect.

**Coverage.** 86 decompositions are computable on the released table, and the identity
$D=C-A=G_l-G_h$ holds to **3.6e-15** in every one of them. Of these, 31 have $D\le0$, i.e. no
fall in the gain, and are not classified below. The remaining **55** split as follows.

| composition of a falling gain | meaning | count |
|---|---|---:|
| **baseline catch-up, $C>A\ge0$** | both arms improve, the baseline more | **47** |
| **intervention-arm degradation, $C>0>A$** | baseline improves while the intervention arm falls | **5** |
| **both arms fall, $A$ further** | $C\le0$ and $A<0$ | **3** |

So where the gain does fall in this archive, the dominant account is **that both arms improve and
the baseline improves more** (47 of 55), while an absolute degradation of the intervention arm
occurs in five cases. This is a statement about the archive, obtained by an identity, and it is
the kind of statement a bare "gain falls with budget" curve cannot make: the curve is consistent
with either account, and here one account is rare.

**One instance where the two columns disagree about the arms.** For
`pcb->neu_det / s2df / 50% / 30->100`, the test column gives $A=-0.302$ with $D=+1.435$, while
the val-best column gives $A=+9.152$ with $D=-0.971$. The two columns therefore disagree not only
about the sign of the gain but about **which arm moved**, which is the finer statement: a
reporting convention here determines the answer to a question about the training dynamics.

**Limits, stated with the result.** (i) The paired counts are mostly 3 to 10, and the intervals
cover data-order randomness only; they are not a statement about population training variance.
(ii) The epoch endpoints are **not uniform** across entries (30->100, 30->200, 50->400 and so on),
so magnitudes must not be compared across rows. (iii) Eight of the twenty largest entries come
from one pair and family, `pcb->neu_det / s2df`, so the count of independent units is far below
the count of entries. (iv) A single cell can yield opposite arm-level readings under the two
columns, so "which arm moved" is not a property of the cell alone. (v) $C$ and $A$ are measured
quantities and do not identify the headroom or mismatch terms that Appendix O discusses; we do
not read them as mechanism.
