#!/usr/bin/env python3
"""Ne and hmF2 against COSMIC-2 for the seven model-only configs of PPT page 7, drawn from adhoc/20261103_cosmic_cfg/tables."""
import csv, gzip, math, datetime as dt, sys
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as md
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
T = '/home/claude/tiegcm-results/adhoc/20261103_cosmic_cfg/tables/'; OUT = sys.argv[1]
CFG = [('A', 'A (2.0, Nick)', '#64748b', 1.6), ('D', 'D (3.0.1)', '#c62828', 1.6), ('C', 'C (3.0.1, heating 4)', '#7b4fc9', 1.0), ('G2', 'G2 (newton an(1) 1.670E-18)', '#a08a00', 1.0),
       ('G3', 'G3 (euveff = 0)', '#0e93b3', 1.0), ('N', 'N (3.0.1 + NCAR settings)', '#b5179e', 1.6), ('N1', 'N1 (3.0.1 + DUFF)', '#17a673', 1.6)]
INK, MUTED, GRID = '#1c2430', '#5a6470', '#e4e6e8'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.linewidth': 0.8, 'savefig.facecolor': 'white'})
when = lambda c: dt.datetime(2022, 1, 1) + dt.timedelta(days=int(c) // 1000 - 1, hours=int(c) % 1000)
MARKS = [(dt.datetime(2022, 7, 7, 0), '7/7 00'), (dt.datetime(2022, 7, 7, 12), 'main phase'), (dt.datetime(2022, 7, 8, 12), 'recovery')]
def dress(ax, top=False):
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for t, lab in MARKS:
        ax.axvline(t, color=MUTED, lw=0.9, ls=':')
        if top: ax.text(t + dt.timedelta(minutes=40), 1.0, lab, transform=ax.get_xaxis_transform(), va='bottom', ha='left', fontsize=9.5, color=MUTED)
    ax.xaxis.set_major_locator(md.HourLocator(byhour=(0, 12))); ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d %H'))
    ax.set_xlim(dt.datetime(2022, 7, 5, 0), dt.datetime(2022, 7, 9, 0))
def key(ax, title, rows):
    ax.text(1.012, 1.02, title, transform=ax.transAxes, va='top', ha='left', fontsize=9.3, color=MUTED, linespacing=1.15)
    y0 = 1.02 - 0.09 * (title.count('\n') + 1) - 0.035
    for i, (col, txt) in enumerate(rows):
        y = y0 - i * 0.112
        ax.plot([1.012, 1.04], [y, y], transform=ax.transAxes, color=col, lw=2.2, clip_on=False, solid_capstyle='round')
        ax.text(1.047, y, txt.replace('-', '−'), transform=ax.transAxes, va='center', ha='left', fontsize=9.6, color=INK, family='DejaVu Sans Mono')
def sgn(v):
    r = int(round(v)); return '0' if r == 0 else (f'+{r}' if r > 0 else f'−{-r}')
def roll(x, w=1):
    k = np.ones(2 * w + 1); return np.convolve(x, k, 'same')
# ---- Ne ----
rows = [r for r in csv.DictReader(gzip.open(T + 'C1_cosmic_cycle_zbin.csv.gz', 'rt')) if r['obs_set'] == 'set4_common']
band = lambda z: '<250' if float(z.split('-')[0]) < 250 else ('250-350' if float(z.split('-')[0]) < 350 else '>350')
cyc = sorted({int(r['cycle']) for r in rows}); ci = {c: i for i, c in enumerate(cyc)}; t = [when(c) for c in cyc]; print('cycles', len(cyc), cyc[0], cyc[-1])
A = {}
for r in rows:
    if r['run'] in [c[0] for c in CFG]:
        a = A.setdefault((r['run'], band(r['zbin_km'])), np.zeros((len(cyc), 4)))
        a[ci[int(r['cycle'])]] += [float(r['n']), float(r['s_obs']), float(r['s_prior']), float(r['ss_dprior'])]
fig, axes = plt.subplots(3, 1, figsize=(13.2, 9.2), sharex=True, gridspec_kw=dict(hspace=0.2, left=0.065, right=0.835, top=0.865, bottom=0.09))
TT = {'>350': 'above 350 km', '250-350': '250–350 km', '<250': 'below 250 km'}
for ax, b in zip(axes, ('>350', '250-350', '<250')):
    o = A[('A', b)]; tab = []
    for k, lab, col, lw in CFG:
        a = A[(k, b)]; assert (a[:, 0] == o[:, 0]).all() and np.allclose(a[:, 1], o[:, 1])
        ax.plot(t, roll(a[:, 2]) / roll(a[:, 0]) / 1e5, color=col, lw=lw, label=lab, zorder=2)
        s = a.sum(0); bi, rm = 100 * (s[2] - s[1]) / s[1], math.sqrt(s[3] / s[0]) / 1e5; tab.append((col, f'{k:<2} {bi:+4.0f}% {rm:.2f}')); print(b, k, f'{bi:+.1f} {rm:.3f}')
    ax.plot(t, roll(o[:, 1]) / roll(o[:, 0]) / 1e5, color='black', lw=1.9, marker='o', ms=2.6, label='COSMIC-2', zorder=3)
    ax.set_ylabel('mean Ne (10$^5$ cm$^{-3}$)'); dress(ax, top=(b == '>350'))
    ax.text(0, 1.025, TT[b], transform=ax.transAxes, va='bottom', fontsize=11.5, color=INK, fontweight='bold'); key(ax, 'whole window\nbias, RMSE (10$^5$)', tab)
h, l = axes[0].get_legend_handles_labels(); order = [7, 0, 1, 2, 3, 4, 5, 6]
fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper left', bbox_to_anchor=(0.06, 0.965), ncol=4, frameon=False, fontsize=10.5, columnspacing=1.6)
fig.suptitle('Ne at COSMIC-2 points, 3-hour running mean: observations and 7 model-only configurations (10-member mean)', x=0.065, y=0.992, ha='left', fontsize=12.5, color=INK)
n = sum(A[('A', b)][:, 0].sum() for b in TT)
fig.text(0.065, 0.012, f'Same {int(n):,} observations for every configuration: all levels not flagged bad in the ionPrf files and with a model value in every run. No DART outlier rejection.\nbias = (model − obs) mean / obs mean.', fontsize=9.5, color=MUTED, linespacing=1.3)
fig.savefig(OUT + '/cosmic2_Ne_seven_configs.png', dpi=170); plt.close(fig)
# ---- hmF2 ----
rows = list(csv.DictReader(gzip.open(T + 'D_cosmic_profiles.csv.gz', 'rt')))
def fl(r, k):
    try: return float(r[k])
    except ValueError: return float('nan')
use = [r for r in rows if int(fl(r, 'n_obs_finite')) == 35 and all(math.isfinite(fl(r, f'{c[0]}_prior_hmf2_km')) for c in CFG)]; print('profiles', len(use))
lat = np.array([fl(r, 'lat_peak') for r in use]); lt = np.array([fl(r, 'lt_peak') for r in use]) % 24; ob = np.array([fl(r, 'obs_hmf2_km') for r in use]); cy = np.array([ci[int(r['cycle'])] for r in use])
M = {c[0]: np.array([fl(r, f'{c[0]}_prior_hmf2_km') for r in use]) for c in CFG}
fig, (a1, a2) = plt.subplots(2, 1, figsize=(13.2, 7.4), sharex=True, gridspec_kw=dict(hspace=0.2, left=0.065, right=0.835, top=0.84, bottom=0.115))
for ax, name, mask in ((a1, 'south of the equator', lat < 0), (a2, 'north of the equator', lat >= 0)):
    i = np.where(mask)[0]; cnt = roll(np.bincount(cy[i], minlength=len(cyc)).astype(float))
    for k, lab, col, lw in CFG: ax.plot(t, roll(np.bincount(cy[i], M[k][i], minlength=len(cyc))) / cnt, color=col, lw=lw, label=lab, zorder=2)
    ax.plot(t, roll(np.bincount(cy[i], ob[i], minlength=len(cyc))) / cnt, color='black', lw=1.9, marker='o', ms=2.6, label='COSMIC-2', zorder=3)
    ax.set_ylabel('mean hmF2 (km)'); dress(ax, top=(ax is a1)); ax.text(0, 1.025, name, transform=ax.transAxes, va='bottom', fontsize=11.5, color=INK, fontweight='bold')
    key(ax, f'whole window, model − obs\n({len(i):,} profiles, km)', [(c[2], f'{c[0]:<2} {(M[c[0]][i] - ob[i]).mean():+6.1f}') for c in CFG])
h, l = a1.get_legend_handles_labels()
fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper left', bbox_to_anchor=(0.06, 0.955), ncol=4, frameon=False, fontsize=10.5, columnspacing=1.6)
fig.suptitle('F-layer peak height (hmF2) at COSMIC-2 profiles, 3-hour running mean: observations and 7 model-only configurations', x=0.065, y=0.99, ha='left', fontsize=12.5, color=INK)
fig.text(0.065, 0.012, f'hmF2 = height of the largest Ne on each profile (10 km levels, 160–500 km), same way for observation and model (10-member mean profile).\n{len(use):,} profiles with observations on all 35 levels; no DART rejection.', fontsize=9.5, color=MUTED, linespacing=1.3)
fig.savefig(OUT + '/cosmic2_hmF2_seven_configs.png', dpi=170); plt.close(fig)
# ---- hmF2 maps ----
latb = np.arange(-40, 41, 10); ltb = np.arange(0, 25, 3)
def cell(d):
    c = np.full((8, 8), np.nan)
    for i in range(8):
        for j in range(8):
            m = (lat >= latb[i]) & (lat < latb[i + 1]) & (lt >= ltb[j]) & (lt < ltb[j + 1])
            if m.sum() >= 30: c[i, j] = d[m].mean()
    return c
cmap = LinearSegmentedColormap.from_list('dv', ['#1c5cab', '#5598e7', '#f0efec', '#eb6834', '#a33a12']); norm = TwoSlopeNorm(0, -70, 70)
pan = [('A (2.0) − COSMIC-2', M['A'] - ob), ('D (3.0.1) − COSMIC-2', M['D'] - ob), ('C (heating 4) − COSMIC-2', M['C'] - ob), ('G2 − COSMIC-2', M['G2'] - ob), ('G3 − COSMIC-2', M['G3'] - ob), ('N (NCAR settings) − COSMIC-2', M['N'] - ob), ('N1 (DUFF) − COSMIC-2', M['N1'] - ob), ('N1 − D (effect of DUFF)', M['N1'] - M['D'])]
fig, axs = plt.subplots(2, 4, figsize=(13.2, 7.2), gridspec_kw=dict(hspace=0.3, wspace=0.09, left=0.055, right=0.925, top=0.885, bottom=0.115))
for ax, (name, d) in zip(axs.ravel(), pan):
    c = cell(d); im = ax.pcolormesh(ltb, latb, c, cmap=cmap, norm=norm, edgecolors='white', linewidth=0.6); print(name, 'range', round(float(np.nanmin(c)), 1), round(float(np.nanmax(c)), 1), 'blank', int(np.isnan(c).sum()))
    for a in range(8):
        for b in range(8):
            if np.isfinite(c[a, b]): ax.text((ltb[b] + ltb[b + 1]) / 2, (latb[a] + latb[a + 1]) / 2, sgn(c[a, b]), ha='center', va='center', fontsize=8.2, color='white' if abs(c[a, b]) > 45 else INK)
    ax.set_title(name, fontsize=10.4, color=INK, loc='left', pad=4); ax.set_xticks(range(0, 25, 6)); ax.set_yticks(range(-40, 41, 20)); ax.tick_params(length=2)
for ax in axs[1]: ax.set_xlabel('local time (h)')
for ax in axs[0]: ax.set_xticklabels([])
for ax in axs[:, 1:].ravel(): ax.set_yticklabels([])
for ax in axs[:, 0]: ax.set_ylabel('latitude (°)')
cax = fig.add_axes([0.937, 0.115, 0.012, 0.77]); cb = fig.colorbar(im, cax=cax); cb.set_label('km', color=INK); cb.ax.tick_params(colors=MUTED, length=2); cb.outline.set_visible(False)
fig.suptitle('hmF2 at COSMIC-2 profiles, by latitude and local time, whole window (7/5 01–7/8 23 UT): mean difference in km', x=0.055, y=0.975, ha='left', fontsize=12.5, color=INK)
fig.text(0.055, 0.012, f'Same {len(use):,} profiles and same hmF2 definition as the time-series figure. Red: model peak above the observed peak.', fontsize=9.5, color=MUTED)
fig.savefig(OUT + '/cosmic2_hmF2_maps_seven_configs.png', dpi=170); plt.close(fig)
