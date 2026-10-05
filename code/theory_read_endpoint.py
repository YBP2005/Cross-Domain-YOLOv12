# -*- coding: utf-8 -*-
"""read_endpoint2.py -- theory read suite, REWRITTEN around the quantities the proof actually uses.

WHY REWRITTEN (seventh external review round, 2026-09-13).  The previous version measured a spectral
suite -- lambda_max, lambda_min, ||H_T||_2, the endpoint Rayleigh quotient Delta^T H_T Delta -- none of
which appears in Corollary 1 or Proposition 1 as stated.  Meanwhile the two scalars the proof does use
were not measured at all:

  (a) the FINITE-SECANT MODULUS at the computed pair,
        mu_sec = 2 [ <grad R_T(theta_S), Delta> - (R_T(theta_S) - R_T(theta_T)) ] / ||Delta||^2,
      which is the largest mu for which the exact ordered-pair inequality used by Proposition 1,
        R_T(theta_S) >= R_T(theta_T) + <grad R_T(theta_T), theta_S - theta_T> + (mu/2)||Delta||^2,
      holds AT THIS PAIR.  An endpoint Hessian Rayleigh quotient is not this quantity: it is based at
      theta_T, while the inequality is based at theta_S.
  (b) the SOURCE-side premises: source optimality R_S(theta_S) - R_S(theta_T) (the linear branch) and
      the directional VI <grad R_S(theta_S), Delta> (the quadratic branch).  These are evaluated on
      the SOURCE corpus -- which this script never touched before -- and a target-gradient norm is
      not a substitute: source stationarity needs grad R_S(theta_S), not grad R_T(theta_S).

Consequently the previous suite could not have falsified H5 in the form the proof uses, and the planned
"branch decision from the sign of lambda_min" was not supportable (lambda_min(theta_T) > 0 does not
establish strong convexity on a ball; lambda_min < 0 does not refute the weaker ordered-pair
inequality).  The spectral quantities are still computed and still reported, but relabelled as
DIAGNOSTICS -- deliberate methodology evidence, not tests of an assumption.

Also added, because endpoint curvature is only a proxy for the curvature ALONG the displacement
(§4.3 says exactly this):
  * the interpolation trace f(t) = R_T(theta_T + t Delta) and f'(t) = <grad R_T(theta_T + t Delta), Delta>
    at t = 0, 1/4, 1/2, 3/4, 1;
  * the weighted segment curvature  mu_seg = (2/||Delta||^2) * integral_0^1 t * Delta^T H_T(theta_T+tDelta) Delta dt,
    which is the exact integral form of mu_sec when the needed differentiability holds -- so mu_seg vs
    mu_sec is a consistency check on the quadratic model, not another spectral number;
  * Ritz residuals for both spectral extremes, so a reported extreme can be distinguished from an
    unconverged one;
  * a per-cell record of whether the source evaluation was possible at all: if the source and target
    class counts differ, the source checkpoint's head is NOT transferred (ultralytics re-initialises
    it), the source risk is not defined at the same head coordinates, and the row says so instead of
    quietly measuring something else.

Delta is restricted to the parameter subspace both checkpoints actually supply.  Read-only: no training,
no checkpoint writes.

Usage:
  python read_endpoint2.py --tag <name> --data <target.yaml> [--src-data <source.yaml>] \
      --src <source.pt> --tgt <endpoint.pt> [--split val] [--draw 0] [--stride 0] \
      [--batch 4] [--nbatches 4] [--lanczos 20] [--out reads.csv]
"""
import argparse, csv, io, os, sys, time
import torch

# Fixed output schema.  NOT recomputed per row: when the source-side keys are conditional (they exist
# only if the source evaluation could be performed at all), a per-row fieldnames list writes a
# different column layout for different rows into the same file, and every later row is silently
# misaligned.  The local test caught exactly that -- a 48-field row under a 53-field header, with
# src_nc_matches reading back a loss value.  The same defect is the root cause of the 18/20/25-field
# convergence CSV earlier.  Every row is therefore padded to this schema and written with it.
SCHEMA = [
    'tag', 'data', 'src_data', 'split', 'draw', 'stride', 'batch', 'nbatches', 'lanczos',
    # target-side quantities the proof uses
    'loss_T', 'loss_S', 'plugin_four', 'gradT_at_S_dot_delta', 'mu_sec',
    'delta_norm', 'missing_src', 'missing_tgt', 'shared_frac', 'nc_src', 'nc_tgt', 'model_nc',
    # source-side premises (only defined when the class counts agree)
    'RS_at_S', 'RS_at_T', 'source_opt_gap', 'gradS_at_S_dot_delta', 'gradS_at_S_norm',
    'src_eval_ok', 'src_nc_matches',
    # interpolation trace and its weighted-curvature integral
    'f_t00', 'f_t25', 'f_t50', 'f_t75', 'f_t100',
    'fp_t00', 'fp_t25', 'fp_t50', 'fp_t75', 'fp_t100',
    'dhd_t00', 'dhd_t25', 'dhd_t50', 'dhd_t75', 'dhd_t100',
    'mu_seg',
    # spectral diagnostics (deliberately NOT described as tests of an assumption)
    'dHd_at_T', 'kappa_minus_T', 'lambda_max', 'lambda_min', 'spec_norm',
    'lanczos_iters', 'ritz_res_max', 'ritz_res_min', 'gradT_at_T_norm',
]

sys.stdout.reconfigure(encoding='utf-8')

SEG = (0.0, 0.25, 0.5, 0.75, 1.0)


def log(msg):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), msg), flush=True)


def batch_loss(tmodel, b):
    """Scalar detection loss for one batch (ultralytics returns a scalar or a component vector)."""
    out = tmodel.loss(b)
    l = out[0] if isinstance(out, (tuple, list)) else out
    l = l.sum() if torch.is_tensor(l) and l.dim() > 0 else l
    return l


def flat_params(model):
    return [p for p in model.parameters() if p.requires_grad]


def set_theta(model, ps, theta):
    with torch.no_grad():
        for p, t in zip(ps, theta):
            p.copy_(t)


def get_theta(ps):
    return [p.detach().clone() for p in ps]


def dot(a, b):
    return float(sum((x * y).sum() for x, y in zip(a, b)).item())


def build_batches(args, data_yaml, split, stride):
    from ultralytics.models.yolo.detect import DetectionTrainer
    from ultralytics.data.utils import check_det_dataset
    overrides = dict(model=args.tgt, data=args.data, imgsz=args.imgsz, batch=args.batch,
                     device=args.device, workers=0, verbose=False, task='detect', mode='train')
    trainer = DetectionTrainer(overrides=overrides)
    trainer.setup_model()
    tmodel = trainer.model
    tmodel.args = trainer.args
    data = check_det_dataset(data_yaml)
    trainer.data = data
    dl = trainer.get_dataloader(data[split], batch_size=args.batch, rank=-1, mode='val')
    batches = []
    for i, b in enumerate(dl):
        if i < stride:
            continue
        batches.append(b)
        if len(batches) >= args.nbatches:
            break
    return tmodel, batches, data


def to_device(tmodel, batches):
    dev = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    tmodel = tmodel.to(dev)
    for b in batches:
        for k in ('img', 'cls', 'bboxes', 'batch_idx'):
            if k in b and torch.is_tensor(b[k]):
                b[k] = b[k].to(dev)
        if 'img' in b and torch.is_tensor(b['img']) and b['img'].dtype == torch.uint8:
            b['img'] = b['img'].float() / 255.0
    return tmodel, batches


def ckpt_nc(path):
    """The class count the CHECKPOINT was trained with.

    This cannot be read off the model: the model is built from the target yaml, so `model.nc` is the
    TARGET's class count no matter which checkpoint was just loaded into it.  Comparing model.nc with
    itself would always say "matches" and would silently defeat the whole class-mismatch guard.  So
    read the checkpoint's own recorded nc.
    """
    try:
        ck = torch.load(path, map_location='cpu', weights_only=False)
    except Exception:
        return None
    m = ck.get('model') if isinstance(ck, dict) else None
    if m is None:
        return None
    for attr in ('nc',):
        v = getattr(m, attr, None)
        if isinstance(v, int) and v > 0:
            return v
    y = getattr(m, 'yaml', None) or {}
    v = y.get('nc') if isinstance(y, dict) else None
    if isinstance(v, int) and v > 0:
        return v
    names = getattr(m, 'names', None)
    if isinstance(names, dict):
        return len(names)
    return None


def load_state(ckpt, tmodel):
    """Load a checkpoint and report which parameters it actually supplied.

    Two things here are corrections rather than conveniences.

    (1) `strict=False` does NOT silently drop a size mismatch -- PyTorch raises RuntimeError for size
        mismatches regardless of `strict`.  An earlier note in this project claimed the opposite; the
        local test of this script falsified it (a 1-class source against a 2-class model crashed on
        load).  So mismatched tensors are filtered out of `sd` BEFORE loading, which is what makes the
        designed behaviour -- restrict Delta to the shared subspace, report the fraction -- reachable
        at all instead of aborting the read.
    (2) `ema` is checked, because ultralytics' own loader prefers it (`ckpt.get("ema") or
        ckpt["model"]`).  On the released checkpoints here `ema` is present but None, so both paths
        resolve to `model`; that is verified rather than assumed, because using a different parameter
        vector than the one the reported metrics came from would silently change every read.
    """
    ck = torch.load(ckpt, map_location='cpu', weights_only=False)
    sd = ck
    if isinstance(ck, dict):
        sd = ck.get('ema') or ck.get('model') or ck
    if hasattr(sd, 'state_dict'):
        sd = sd.state_dict()
    sd = {k: v for k, v in sd.items() if torch.is_tensor(v)}
    named = [(n, p) for n, p in tmodel.named_parameters() if p.requires_grad]
    shared = [bool(n in sd and tuple(sd[n].shape) == tuple(p.shape)) for n, p in named]
    ok = set(n for (n, p), sh in zip(named, shared) if sh)
    sd = {k: v for k, v in sd.items() if k in ok}       # never hand PyTorch a size mismatch
    missing, unexpected = tmodel.load_state_dict(sd, strict=False)
    return tmodel, len(missing), len(unexpected), shared


def instrument_mode(tmodel):
    """The mode in which the detection LOSS is meaningful, made deterministic.

    `DetectionModel.loss()` is the training objective, and `Detect.forward` only returns the raw
    per-scale predictions the loss consumes when the module is in TRAIN mode; in EVAL mode it runs
    inference/NMS and what comes back is not the training risk at all.  Measured on one released
    endpoint at one fixed state: R(theta_T) = 6.03 in train mode versus 66.0 in eval mode -- a factor
    of ten, i.e. evaluating the risk in eval mode is simply wrong.

    But leaving BatchNorm in train mode makes the risk depend on the running-statistics history, so
    repeated evaluations are not evaluations of one fixed function.  Hence: the model in train mode,
    every BatchNorm module in eval mode.  The Detect head keeps train semantics (raw predictions), the
    normalisation layers use their running statistics, and the value is reproducible.
    """
    import torch.nn as nn
    tmodel.train()
    for m in tmodel.modules():
        if isinstance(m, nn.modules.batchnorm._BatchNorm):
            m.eval()
    return tmodel


def mean_loss(tmodel, batches):
    tot = 0.0
    for b in batches:
        tot = tot + batch_loss(tmodel, b)
    return tot / float(len(batches))


def loss_and_grad(tmodel, batches, ps, create_graph=False):
    l = mean_loss(tmodel, batches)
    g = torch.autograd.grad(l, ps, create_graph=create_graph, retain_graph=create_graph)
    return float(l.item()), ([gi.detach() for gi in g] if not create_graph else g)


def delta_curvature(tmodel, batches, ps, delta):
    """Delta^T H Delta at the model's CURRENT parameters (one HVP)."""
    l = mean_loss(tmodel, batches)
    g = torch.autograd.grad(l, ps, create_graph=True, retain_graph=True)
    gd = sum((gi * di).sum() for gi, di in zip(g, delta))
    hv = torch.autograd.grad(gd, ps, retain_graph=False, allow_unused=True)
    hv = [h if h is not None else torch.zeros_like(p) for h, p in zip(hv, ps)]
    return dot(delta, hv)


def lanczos_reads(tmodel, batches, ps, delta, iters):
    """Lanczos on the target-loss Hessian at the current parameters.

    Returns the Ritz extremes WITH their residuals: a reported extreme whose residual is not small is
    an unconverged number, and that must be visible in the output rather than assumed away.
    """
    l = mean_loss(tmodel, batches)
    g = torch.autograd.grad(l, ps, create_graph=True, retain_graph=True)

    def hvp(vec):
        d = sum((gi * vi).sum() for gi, vi in zip(g, vec))
        hv = torch.autograd.grad(d, ps, retain_graph=True, allow_unused=True)
        return [h if h is not None else torch.zeros_like(p) for h, p in zip(hv, ps)]

    q = [torch.randn_like(p) for p in ps]
    nq = torch.sqrt(sum((qi * qi).sum() for qi in q))
    q = [qi / nq for qi in q]
    q_prev = [torch.zeros_like(p) for p in ps]
    beta_prev = 0.0
    alphas, betas = [], []
    basis = []                      # KEEP the Krylov basis: a Ritz vector is only meaningful in it
    for _ in range(iters):
        basis.append(q)
        z = hvp(q)
        alpha = dot(q, z)
        alphas.append(alpha)
        z = [zi - alpha * qi - beta_prev * qpi for zi, qi, qpi in zip(z, q, q_prev)]
        beta = float(torch.sqrt(sum((zi * zi).sum() for zi in z)).item())
        if beta < 1e-12:
            break
        betas.append(beta)
        q_prev = q
        q = [zi / beta for zi in z]
        beta_prev = beta
    m = len(alphas)
    T = torch.zeros(m, m, dtype=torch.float64)
    for i in range(m):
        T[i, i] = alphas[i]
        if i + 1 < m:
            T[i, i + 1] = betas[i]
            T[i + 1, i] = betas[i]
    ev, evec = torch.linalg.eigh(T)
    lam_max = float(ev[-1].item())
    lam_min = float(ev[0].item())

    def residual(idx):
        """||H v - lam v|| for the Ritz pair, v rebuilt from the SAME Krylov basis that produced T.

        (An earlier draft rebuilt the basis by re-running the recurrence from a fresh random start,
        which gives a different subspace and makes the residual meaningless.)
        """
        y = evec[:, idx]
        v = [torch.zeros_like(p) for p in ps]
        for j in range(len(basis)):
            v = [vi + float(y[j]) * qji for vi, qji in zip(v, basis[j])]
        vn = float(torch.sqrt(sum((vi * vi).sum() for vi in v)).item())
        if vn < 1e-30:
            return float('nan')
        v = [vi / vn for vi in v]
        hv = hvp(v)
        lam = lam_max if idx == m - 1 else lam_min
        r = [hi - lam * vi for hi, vi in zip(hv, v)]
        return float(torch.sqrt(sum((ri * ri).sum() for ri in r)).item())

    try:
        res_max = residual(m - 1)
        res_min = residual(0)
    except Exception as ex:
        log('  WARN ritz residual failed: %s' % ex)
        res_max = res_min = float('nan')
    return g, lam_max, lam_min, m, res_max, res_min


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--data', required=True, help='target corpus yaml')
    ap.add_argument('--src-data', default='', help='SOURCE corpus yaml (for the source-side premises)')
    ap.add_argument('--src', required=True)
    ap.add_argument('--tgt', required=True)
    ap.add_argument('--split', default='val')
    ap.add_argument('--src-split', default='')
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--batch', type=int, default=4)
    ap.add_argument('--nbatches', type=int, default=4)
    ap.add_argument('--lanczos', type=int, default=20)
    ap.add_argument('--device', default='0')
    ap.add_argument('--out', default='/workspace/theory_reads.csv')
    ap.add_argument('--draw', type=int, default=0)
    ap.add_argument('--stride', type=int, default=0)
    ap.add_argument('--no-segment', action='store_true',
                    help='skip the interpolation trace (it is 5 losses, 5 grads and 5 HVPs)')
    args = ap.parse_args()

    row = dict(tag=args.tag, data=os.path.basename(args.data),
               src_data=os.path.basename(args.src_data) if args.src_data else '',
               split=args.split, draw=args.draw, stride=args.stride,
               batch=args.batch, nbatches=args.nbatches, lanczos=args.lanczos)

    log('building model + %d target batches from %s' % (args.nbatches, args.data))
    tmodel, batches, tdata = build_batches(args, args.data, args.split, args.stride)
    tmodel, batches = to_device(tmodel, batches)
    ps = flat_params(tmodel)

    src_batches = None
    if args.src_data:
        ssplit = args.src_split or args.split
        try:
            _m, src_batches, sdata = build_batches_for_source(args, ssplit)
            log('source batches: %d from %s' % (len(src_batches), args.src_data))
        except Exception as ex:
            log('  WARN could not build source batches: %s: %s' % (type(ex).__name__, ex))
            src_batches = None

    # ---- endpoint T ----
    tmodel, miss_t, unexp_t, shared_T = load_state(args.tgt, tmodel)
    instrument_mode(tmodel)
    RT_at_T, _ = loss_and_grad(tmodel, batches, ps)
    theta_T = get_theta(ps)
    nc_ckpt_tgt = ckpt_nc(args.tgt)

    # ---- endpoint S ----
    tmodel, miss_s, unexp_s, shared_S = load_state(args.src, tmodel)
    instrument_mode(tmodel)
    RT_at_S, gT_at_S = loss_and_grad(tmodel, batches, ps)
    theta_S = get_theta(ps)
    nc_ckpt_src = ckpt_nc(args.src)

    shared = [a and b for a, b in zip(shared_S, shared_T)]
    shared_frac = sum(shared) / float(len(shared))
    delta = [((s - t) if sh else torch.zeros_like(t)) for s, t, sh in zip(theta_S, theta_T, shared)]
    dnorm2 = float(sum((d ** 2).sum() for d in delta).item())
    dnorm = dnorm2 ** 0.5

    plugin_four = RT_at_S - RT_at_T                                  # (4)hat = R_T(theta_S) - R_T(theta_T)
    gT_dot_delta = dot(gT_at_S, delta)                               # <grad R_T(theta_S), Delta>
    mu_sec = (2.0 * (gT_dot_delta - plugin_four) / dnorm2) if dnorm2 > 0 else float('nan')
    row.update(loss_T=RT_at_T, loss_S=RT_at_S, plugin_four=plugin_four,
               gradT_at_S_dot_delta=gT_dot_delta, mu_sec=mu_sec,
               delta_norm=dnorm, missing_src=miss_s, missing_tgt=miss_t,
               shared_frac=round(shared_frac, 6), nc_src=nc_ckpt_src, nc_tgt=nc_ckpt_tgt,
               model_nc=getattr(tmodel, 'nc', ''))

    # ---- source-side premises, on the SOURCE corpus, only if the parameters live in one space ----
    src_ok = False
    nc_match = bool(nc_ckpt_src is not None and nc_ckpt_tgt is not None
                    and nc_ckpt_src == nc_ckpt_tgt)
    if src_batches is not None:
        if nc_match:
            tmodel, src_batches = to_device(tmodel, src_batches)
            set_theta(tmodel, ps, theta_S)
            RS_at_S, gS_at_S = loss_and_grad(tmodel, src_batches, ps)
            set_theta(tmodel, ps, theta_T)
            RS_at_T, _ = loss_and_grad(tmodel, src_batches, ps)
            src_ok = True
            row.update(RS_at_S=RS_at_S, RS_at_T=RS_at_T,
                       source_opt_gap=RS_at_S - RS_at_T,
                       gradS_at_S_dot_delta=dot(gS_at_S, delta),
                       gradS_at_S_norm=(sum((gi ** 2).sum() for gi in gS_at_S) ** 0.5).item())
        else:
            # Different class counts: ultralytics rebuilt the head, so the source checkpoint does NOT
            # supply the head the target model has.  The source risk is then not a function on this
            # parameter space, and evaluating it would be measuring a different object.  Say so.
            log('  source evaluation SKIPPED: checkpoint nc %s (src) != %s (tgt); head not transferred'
                % (nc_ckpt_src, nc_ckpt_tgt))
    row['src_eval_ok'] = int(src_ok)
    row['src_nc_matches'] = int(nc_match)

    # ---- interpolation trace along the displacement ----
    # dHd at theta_T is computed unconditionally: it is the endpoint diagnostic, and mu_seg needs it
    # as the t = 0 node of the quadrature.
    set_theta(tmodel, ps, theta_T)
    dHd_at_T = delta_curvature(tmodel, batches, ps, delta)
    if not args.no_segment:
        f, fp, dhd_seg = {}, {}, {0.0: dHd_at_T}
        for t in SEG[1:]:
            pt = [ti + t * di for ti, di in zip(theta_T, delta)]
            set_theta(tmodel, ps, pt)
            lt, gt = loss_and_grad(tmodel, batches, ps)
            f[t] = lt
            fp[t] = dot(gt, delta)
            if t < 1.0:
                dhd_seg[t] = delta_curvature(tmodel, batches, ps, delta)
        set_theta(tmodel, ps, theta_S)
        dhd_seg[1.0] = delta_curvature(tmodel, batches, ps, delta)
        # f(0) and f'(0) are the target endpoint, already measured
        f[0.0] = RT_at_T
        fp[0.0] = 0.0                     # placeholder; filled from the gradient at theta_T below
        set_theta(tmodel, ps, theta_T)
        _l0, g0 = loss_and_grad(tmodel, batches, ps)
        fp[0.0] = dot(g0, delta)
        for t in SEG:
            row['f_t%02d' % int(t * 100)] = f[t]
            row['fp_t%02d' % int(t * 100)] = fp[t]
            row['dhd_t%02d' % int(t * 100)] = dhd_seg.get(t, float('nan'))
        # trapezoid on t*q(t) with h=0.25 -> the integral form of mu_sec
        h = 0.25
        q = [dhd_seg[t] for t in SEG]
        integ = h * (0.5 * (SEG[0] * q[0]) + sum(SEG[i] * q[i] for i in (1, 2, 3)) + 0.5 * (SEG[4] * q[4]))
        row['mu_seg'] = (2.0 * integ / dnorm2) if dnorm2 > 0 else float('nan')
        log('  segment: mu_seg=%.6g  mu_sec=%.6g' % (row['mu_seg'], mu_sec))
    else:
        for t in SEG:
            row['f_t%02d' % int(t * 100)] = float('nan')
            row['fp_t%02d' % int(t * 100)] = float('nan')
            row['dhd_t%02d' % int(t * 100)] = float('nan')
        row['mu_seg'] = float('nan')

    # ---- spectral diagnostics at theta_T (deliberately labelled diagnostics) ----
    set_theta(tmodel, ps, theta_T)
    instrument_mode(tmodel)
    log('Lanczos (%d iters) at the target endpoint (mode: train + frozen BN)' % args.lanczos)
    gvec, lam_max, lam_min, m, res_max, res_min = lanczos_reads(tmodel, batches, ps, delta, args.lanczos)
    row.update(lanczos_iters=m, lambda_max=lam_max, lambda_min=lam_min,
               spec_norm=max(lam_max, -lam_min), ritz_res_max=res_max, ritz_res_min=res_min,
               gradT_at_T_norm=(sum((gi ** 2).sum() for gi in gvec) ** 0.5).item(),
               dHd_at_T=dHd_at_T,
               kappa_minus_T=max(0.0, -dHd_at_T / dnorm2) if dnorm2 > 0 else float('nan'))

    # ---- write, padded to the fixed schema so rows cannot be misaligned ----
    padded = {k: row.get(k, '') for k in SCHEMA}
    for k in row:
        if k not in SCHEMA:
            log('WARN row key not in SCHEMA, dropped from the CSV: %s' % k)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    new = not os.path.exists(args.out)
    with io.open(args.out, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA, restval='')
        if new:
            w.writeheader()
        w.writerow(padded)
    log('WROTE %s' % args.out)
    for k in ('plugin_four', 'mu_sec', 'mu_seg', 'gT_dot_delta', 'source_opt_gap',
              'gradS_at_S_dot_delta', 'lambda_max', 'lambda_min', 'ritz_res_max', 'ritz_res_min',
              'shared_frac', 'src_eval_ok'):
        log('   %-22s %s' % (k, row.get(k)))


def build_batches_for_source(args, split):
    """Batches from the SOURCE corpus, using the same fixed-draw convention as the target batches.

    A throwaway DetectionTrainer is used only to obtain an identically-configured dataloader; its
    parameters are never used, so it is deleted before returning to keep VRAM free for the reads.
    """
    from ultralytics.models.yolo.detect import DetectionTrainer
    from ultralytics.data.utils import check_det_dataset
    overrides = dict(model=args.tgt, data=args.src_data, imgsz=args.imgsz, batch=args.batch,
                     device=args.device, workers=0, verbose=False, task='detect', mode='train')
    trainer = DetectionTrainer(overrides=overrides)
    trainer.setup_model()
    throwaway = trainer.model
    data = check_det_dataset(args.src_data)
    trainer.data = data
    key = split if split in data else ('val' if 'val' in data else 'train')
    dl = trainer.get_dataloader(data[key], batch_size=args.batch, rank=-1, mode='val')
    batches = []
    for i, b in enumerate(dl):
        if i < args.stride:
            continue
        batches.append(b)
        if len(batches) >= args.nbatches:
            break
    del throwaway, trainer
    try:
        torch.cuda.empty_cache()
    except Exception:
        pass
    return None, batches, data


if __name__ == '__main__':
    main()
