#!/usr/bin/env python3
"""Ne and F-layer peak height against COSMIC-2 for the three control runs, drawn from the
results-repo tables (no new model output). Colours and time markers follow PPT page 7."""
import csv, gzip, math, collections, datetime as dt, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.text
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

T = '/home/claude/tiegcm-results/deep/20261102_duff1101_check/tables/'
OUT = sys.argv[1]
RUNS = [('ctrl95', 'A (2.0)', '#64748b'), ('v3ctrl', 'D (3.0.1 default)', '#c62828'), ('v3ctrl_duff', 'N1 (3.0.1 + DUFF)', '#17a673')]
SHORT = {'ctrl95': 'A', 'v3ctrl': 'D', 'v3ctrl_duff': 'N1'}
INK, MUTED, GRID = '#1c2430', '#5a6470', '#e4e6e8'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.linewidth': 0.8, 'savefig.facecolor': 'white'})

def when(c):
    c = int(c)
    return dt.datetime(2022, 1, 1) + dt.timedelta(days=c // 1000 - 1, hours=c % 1000)

MARKS = [(dt.datetime(2022, 7, 7, 0), '7/7 00'), (dt.datetime(2022, 7, 7, 12), 'main phase'), (dt.datetime(2022, 7, 8, 12), 'recovery')]

def dress(ax, top=False):
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for t, lab in MARKS:
        ax.axvline(t, color=MUTED, lw=0.9, ls=':')
        if top:
            ax.text(t + dt.timedelta(minutes=40), 1.0, lab, transform=ax.get_xaxis_transform(), va='bottom', ha='left', fontsize=9.5, color=MUTED)
    ax.xaxis.set_major_locator(md.HourLocator(byhour=(0, 12)))
    ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d %H'))
    ax.set_xlim(dt.datetime(2022, 7, 5, 0), dt.datetime(2022, 7, 9, 0))

def fits(fig, name):
    fig.canvas.draw(); r = fig.canvas.get_renderer(); W, H = fig.canvas.get_width_height()
    bad = [t.get_text()[:40] for t in fig.findobj(matplotlib.text.Text) if t.get_text() and (lambda b: b.x1 > W or b.x0 < 0 or b.y0 < 0 or b.y1 > H)(t.get_window_extent(r))]
    print(name, 'text outside the figure:', bad)

def sgn(v):
    r = int(round(v))
    return '0' if r == 0 else (f'+{r}' if r > 0 else f'\u2212{-r}')

def key(ax, title, rows):
    """Full-window numbers beside the panel: a coloured stroke carries identity, the text stays in ink."""
    ax.text(1.012, 0.97, title, transform=ax.transAxes, va='top', ha='left', fontsize=9.5, color=MUTED)
    n_title = title.count('\n') + 1
    for i, (col, txt) in enumerate(rows):
        y = 0.97 - 0.085 * n_title - 0.03 - i * 0.115
        ax.plot([1.012, 1.04], [y, y], transform=ax.transAxes, color=col, lw=2.2, clip_on=False, solid_capstyle='round')
        ax.text(1.047, y, txt.replace('-', '\u2212'), transform=ax.transAxes, va='center', ha='left', fontsize=10, color=INK, family='DejaVu Sans Mono')

# ---------- Ne against COSMIC-2 ----------
rows = [r for r in csv.DictReader(gzip.open(T + 'C1_cosmic_cycle_zbin.csv.gz', 'rt')) if r['obs_set'] == 'set1_all6']
def band(z):
    lo = float(z.split('-')[0])
    return '<250' if lo < 250 else ('250-350' if lo < 350 else '>350')
cycles = sorted({int(r['cycle']) for r in rows}); ci = {c: i for i, c in enumerate(cycles)}; t = [when(c) for c in cycles]
A = {}
for r in rows:
    if r['run'] not in SHORT: continue
    a = A.setdefault((r['run'], band(r['zbin_km'])), np.zeros((len(cycles), 4)))
    a[ci[int(r['cycle'])]] += [float(r['n']), float(r['s_obs']), float(r['s_prior']), float(r['ss_dprior'])]
fig, axes = plt.subplots(3, 1, figsize=(13.2, 8.6), sharex=True, gridspec_kw=dict(hspace=0.2, left=0.065, right=0.835, top=0.89, bottom=0.095))
TITLES = {'>350': 'above 350 km', '250-350': '250–350 km', '<250': 'below 250 km'}
checks = {}
for ax, b in zip(axes, ('>350', '250-350', '<250')):
    obs = A[('ctrl95', b)]
    for run, lab, col in RUNS:
        a = A[(run, b)]; assert (a[:, 0] == obs[:, 0]).all() and np.allclose(a[:, 1], obs[:, 1])
        ax.plot(t, a[:, 2] / a[:, 0] / 1e5, color=col, lw=1.5, label=lab, zorder=2)
    ax.plot(t, obs[:, 1] / obs[:, 0] / 1e5, color='black', lw=1.9, marker='o', ms=3, label='COSMIC-2', zorder=3)
    ax.set_ylabel('mean Ne (10$^5$ cm$^{-3}$)'); dress(ax, top=(b == '>350'))
    ax.text(0.0, 1.025, TITLES[b], transform=ax.transAxes, va='bottom', fontsize=11.5, color=INK, fontweight='bold')
    table = []
    for run, lab, col in RUNS:
        a = A[(run, b)].sum(0); bias = 100 * (a[2] - a[1]) / a[1]; rmse = math.sqrt(a[3] / a[0]) / 1e5
        checks[(run, b)] = (bias, rmse); table.append((col, f'{SHORT[run]:<2} {bias:+4.0f}%  {rmse:.2f}'))
    key(ax, 'whole window\nbias, RMSE (10$^5$)', table)
h, l = axes[0].get_legend_handles_labels(); order = [3, 0, 1, 2]
fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper left', bbox_to_anchor=(0.06, 0.965), ncol=4, frameon=False, fontsize=11)
fig.suptitle('Ne at COSMIC-2 points, mean of each 1-hour cycle: observations and control-run 1-hour forecasts (10-member mean)', x=0.065, y=0.992, ha='left', fontsize=12.5, color=INK)
n_all = sum(float(r['n_all']) for r in csv.DictReader(gzip.open(T + 'C3_cosmic_qc_counts.csv.gz', 'rt')) if r['run'] == 'ctrl95')
n_use = sum(A[('ctrl95', b)][:, 0].sum() for b in TITLES)
print('Ne observations used', int(n_use), 'of', int(n_all), f'{100 * n_use / n_all:.1f}%')
fig.text(0.065, 0.012, f'Same {int(n_use):,} observations for every run ({100 * n_use / n_all:.0f}% of all {int(n_all):,}): only those DART accepted in all six control and assimilation runs, so points rejected as outliers in any run are left out.\nbias = (model − obs) mean / obs mean.', fontsize=9.5, color=MUTED, linespacing=1.3)
fits(fig, 'Ne'); fig.savefig(OUT + '/cosmic2_Ne_three_controls.png', dpi=170); plt.close(fig)
for k, v in sorted(checks.items()): print('Ne', k, f'bias {v[0]:+.1f}%  rmse {v[1]:.3f}')

# ---------- F-layer peak height against COSMIC-2 ----------
rows = list(csv.DictReader(gzip.open(T + 'D_cosmic_profiles.csv.gz', 'rt')))
def fin(r, k):
    try: return math.isfinite(float(r[k]))
    except ValueError: return False
use = [r for r in rows if int(float(r['n_obs_finite'])) == 35 and fin(r, 'obs_hmf2_km') and all(fin(r, f'{k}_prior_hmf2_km') for k in SHORT)]
print('profiles', len(use), 'of', len(rows))
for k in SHORT:
    z = [r for r in use if float(r[f'{k}_n_qc_pass']) == 0]
    print(k, 'profiles with no accepted level', len(z))
none = [r for r in use if all(float(r[f'{k}_n_qc_pass']) == 0 for k in SHORT)]
keep = [r for r in use if not all(float(r[f'{k}_n_qc_pass']) == 0 for k in SHORT)]
print('no accepted level in all three controls', len(none), 'of which obs peak outside 200-450:', sum(1 for r in none if not 200 <= float(r['obs_hmf2_km']) < 450))
for k in SHORT:
    print('without those', k, 'all', round(sum(float(r[f'{k}_prior_hmf2_km']) - float(r['obs_hmf2_km']) for r in keep) / len(keep), 1),
          'S', round(np.mean([float(r[f'{k}_prior_hmf2_km']) - float(r['obs_hmf2_km']) for r in keep if float(r['lat_peak']) < 0]), 1),
          'N', round(np.mean([float(r[f'{k}_prior_hmf2_km']) - float(r['obs_hmf2_km']) for r in keep if float(r['lat_peak']) >= 0]), 1))
lat = np.array([float(r['lat_peak']) for r in use]); lt = np.array([float(r['lt_peak']) for r in use]) % 24
cyc = np.array([ci[int(r['cycle'])] for r in use]); ob = np.array([float(r['obs_hmf2_km']) for r in use])
M = {k: np.array([float(r[f'{k}_prior_hmf2_km']) for r in use]) for k in SHORT}
fig = plt.figure(figsize=(13.2, 10.4))
gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 1.05], hspace=0.30, wspace=0.09, left=0.065, right=0.835, top=0.915, bottom=0.09)
ax1 = fig.add_subplot(gs[0, :]); ax2 = fig.add_subplot(gs[1, :], sharex=ax1)
for ax, name, mask in ((ax1, 'south of the equator', lat < 0), (ax2, 'north of the equator', lat >= 0)):
    idx = np.where(mask)[0]; n = np.bincount(cyc[idx], minlength=len(cycles)).astype(float)
    for run, lab, col in RUNS:
        ax.plot(t, np.bincount(cyc[idx], M[run][idx], minlength=len(cycles)) / n, color=col, lw=1.5, label=lab, zorder=2)
    ax.plot(t, np.bincount(cyc[idx], ob[idx], minlength=len(cycles)) / n, color='black', lw=1.9, marker='o', ms=3, label='COSMIC-2', zorder=3)
    ax.set_ylabel('mean hmF2 (km)'); dress(ax, top=(ax is ax1))
    ax.text(0.0, 1.025, name, transform=ax.transAxes, va='bottom', fontsize=11.5, color=INK, fontweight='bold')
    key(ax, f'whole window, model − obs\n({len(idx):,} profiles)', [(col, f'{SHORT[run]:<2} {(M[run][idx] - ob[idx]).mean():+5.1f} km') for run, lab, col in RUNS])
plt.setp(ax1.get_xticklabels(), visible=False)
h, l = ax1.get_legend_handles_labels(); order = [3, 0, 1, 2]
fig.legend([h[i] for i in order], [l[i] for i in order], loc='upper left', bbox_to_anchor=(0.06, 0.976), ncol=4, frameon=False, fontsize=11)
# where in latitude and local time
latb = np.arange(-40, 41, 10); ltb = np.arange(0, 25, 3)
def cell(d):
    c = np.full((len(latb) - 1, len(ltb) - 1), np.nan); cnt = np.zeros_like(c)
    for i in range(len(latb) - 1):
        for j in range(len(ltb) - 1):
            m = (lat >= latb[i]) & (lat < latb[i + 1]) & (lt >= ltb[j]) & (lt < ltb[j + 1])
            cnt[i, j] = m.sum()
            if m.sum() >= 30: c[i, j] = d[m].mean()
    return c, cnt
print('profiles outside the map latitude range', int(((lat < -40) | (lat >= 40)).sum()))
cmap = LinearSegmentedColormap.from_list('dv', ['#1c5cab', '#5598e7', '#f0efec', '#eb6834', '#a33a12'])
norm = TwoSlopeNorm(0, -70, 70)
panels = [('A: 2.0 − COSMIC-2', M['ctrl95'] - ob), ('D: 3.0.1 default − COSMIC-2', M['v3ctrl'] - ob), ('N1: 3.0.1 + DUFF − COSMIC-2', M['v3ctrl_duff'] - ob), ('N1 − D (DUFF effect)', M['v3ctrl_duff'] - M['v3ctrl'])]
for j, (name, d) in enumerate(panels):
    ax = fig.add_subplot(gs[2, j]); c, cnt = cell(d)
    if j == 0: print('profiles per cell: min', int(cnt.min()), 'median', int(np.median(cnt)), 'cells under 30:', int((cnt < 30).sum()))
    print(name, 'cell range', round(float(np.nanmin(c)), 1), round(float(np.nanmax(c)), 1))
    im = ax.pcolormesh(ltb, latb, c, cmap=cmap, norm=norm, edgecolors='white', linewidth=0.6)
    for a in range(c.shape[0]):
        for b in range(c.shape[1]):
            if np.isfinite(c[a, b]):
                ax.text((ltb[b] + ltb[b + 1]) / 2, (latb[a] + latb[a + 1]) / 2, sgn(c[a, b]), ha='center', va='center', fontsize=7.8, color='white' if abs(c[a, b]) > 45 else INK)
    ax.set_title(name, fontsize=10.2, color=INK, loc='left', pad=4); ax.set_xticks(range(0, 25, 6)); ax.set_xlabel('local time (h)')
    ax.tick_params(length=2)
    if j: ax.set_yticklabels([])
    else: ax.set_ylabel('latitude (°)')
    ax.set_yticks(range(-40, 41, 20))
cax = fig.add_axes([0.847, 0.09, 0.012, 0.236]); cb = fig.colorbar(im, cax=cax); cb.set_label('km', color=INK); cb.ax.tick_params(colors=MUTED, length=2); cb.outline.set_visible(False)
fig.suptitle('F-layer peak height (hmF2) at COSMIC-2 profiles: observations and control-run 1-hour forecasts (10-member mean)', x=0.065, y=0.995, ha='left', fontsize=12.5, color=INK)
fig.text(0.065, 0.012, f'hmF2 = height of the largest Ne on each profile (10 km levels, 160–500 km), same way for observation and model.\n{len(use):,} profiles with observations on all 35 levels; no DART rejection applied.', fontsize=9.5, color=MUTED, linespacing=1.3)
fits(fig, 'hmF2'); fig.savefig(OUT + '/cosmic2_hmF2_three_controls.png', dpi=170); plt.close(fig)
