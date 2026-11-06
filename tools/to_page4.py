#!/usr/bin/env python3
"""Add the fields themselves (not differences) to data/full/ from the 2026-11-06 export (web_export3, part c):
maps_own_<F>_<cfg>.json for the 16 configurations and 6 DART runs, ht_own_<cfg>.json, and an 'own' block in index.json.
usage: python3 -I to_page4.py EXPORT3_DIR DATA_DIR
Encoding of a map: value = lo + code*s (TN K, hmF2 km) or 10^(lo + code*s) (DEN kg m-3, NE cm-3, NmF2 cm-3); code 255 = no value.
DEN is converted from g cm-3 (export) to kg m-3 here (+3 in log10; x1000 in the height-time files)."""
import base64, gzip, json, os, sys
import numpy as np
E, D = sys.argv[1:3]
idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
tmpl = json.load(open(f'{D}/maps_TN_D-C.json', encoding='utf-8'))
pack = lambda raw: base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode()
def delta(u, C=144):
    a = u.reshape(-1, C).copy(); a[:, 1:] = (a[:, 1:].astype(int) - a[:, :-1].astype(int)) & 255; return a.astype(np.uint8).tobytes()
LOG = {'DEN', 'NE', 'NmF2'}
UNIT = {'TN': 'K', 'DEN': 'kg m⁻³', 'NE': 'cm⁻³', 'hmF2': 'km', 'NmF2': 'cm⁻³'}
HT_UNIT = {'TN': 'K', 'UN': 'm/s', 'VN': 'm/s', 'O2': 'mmr', 'O1': 'mmr', 'N2': 'mmr', 'OP': 'cm⁻³', 'HE': 'mmr', 'NO': 'mmr', 'NO_COOL': 'erg g⁻¹ s⁻¹', 'O_N2': '', 'NE': 'cm⁻³', 'DEN': 'kg m⁻³'}
HT_FIELDS = idx['ht_fields']; STATS = ['mean', 'min', 'max', 'cov']
cfgs = [f[len('maps_TN_'):-4] for f in sorted(os.listdir(E)) if f.startswith('maps_TN_') and '-' not in f[len('maps_TN_'):]]
own = {'configs': {}, 'range': {}, 'log': sorted(LOG), 'units': UNIT, 'ht_units': HT_UNIT, 'ht_stats': STATS,
       'definition': '10-member mean of the field itself at fixed heights (hmF2/NmF2: peak over levels at or above 200 km); maps_own encode value = lo + code*scale, or 10^(lo + code*scale) for the log fields; code 255 = no value. Height-time: area-weighted global mean, min and max of the member-mean field over the covered grid points, and coverage (%) of the globe; DEN in kg m-3.'}
size = 0; n = 0
for cfg in cfgs:
    ent = {'maps': {}}
    for F in idx['map_fields']:
        z = np.load(f'{E}/maps_{F}_{cfg}.npz', allow_pickle=False)
        keys = [F] if F in ('hmF2', 'NmF2') else [f'{F}_{k}' for k in idx['km_maps']]
        lo = [float(z[k + '_lo']) + (3.0 if F == 'DEN' else 0.0) for k in keys]; sc = [float(z[k + '_scale']) for k in keys]
        u = np.concatenate([z[k].ravel() for k in keys])
        J = {'cfg': cfg, 'field': F, 'shape': list(z[keys[0]].shape), 'km': ['peak'] if len(keys) == 1 else list(idx['km_maps']), 'lo': lo, 'scale': sc,
             'log': F in LOG, 'unit': UNIT[F], 'time_source': [int(x) for x in z['time_source']],
             'order': 'codes at each km; each (time, lat, lt) C order', 'encoding': tmpl['encoding'], 'b64': pack(delta(u))}
        name = f'maps_own_{F}_{cfg}.json'; txt = json.dumps(J, ensure_ascii=False, separators=(',', ':')); open(f'{D}/{name}', 'w', encoding='utf-8').write(txt)
        size += len(txt.encode()); n += 1; ent['maps'][F] = name
        for k, l, s in zip(keys, lo, sc):
            h = np.bincount(z[k].ravel(), minlength=256)[:255].astype(np.int64); c = np.cumsum(h); tot = int(c[-1])
            p1 = int(np.searchsorted(c, 0.01 * tot)); p99 = int(np.searchsorted(c, 0.99 * tot))
            own['range'].setdefault(k, {})[cfg] = [l, l + 254 * s, l + p1 * s, l + p99 * s]   # encoding range, then 1st and 99th percentile of the values
    z = np.load(f'{E}/ht_{cfg}.npz', allow_pickle=False)
    assert [float(x) for x in z['km']] == [float(x) for x in idx['km_ht']]
    arrs = []
    for f in HT_FIELDS:
        for s in STATS:
            a = np.asarray(z[f'{f}_{s}'], dtype='<f4')
            if f == 'DEN' and s != 'cov': a = a * np.float32(1000.0)
            arrs.append(a.tobytes())
    J = {'cfg': cfg, 'shape': list(z['TN_mean'].shape), 'fields': HT_FIELDS, 'stats': STATS, 'order': 'field-major, then stat; each (time, km)',
         'encoding': 'float32 little-endian, gzip, base64', 'time_source': [int(x) for x in z['time_source']], 'b64': pack(b''.join(arrs))}
    name = f'ht_own_{cfg}.json'; txt = json.dumps(J, ensure_ascii=False, separators=(',', ':')); open(f'{D}/{name}', 'w', encoding='utf-8').write(txt)
    size += len(txt.encode()); n += 1; ent['ht'] = name; ent['ht_time_source'] = J['time_source']
    own['configs'][cfg] = ent
idx['own'] = own
idx['source']['update4'] = 'fields themselves (maps_own_*, ht_own_*) for 16 configurations and 6 DART runs, from adhoc/20261106_web_export3 part c (results repo commit 8e880ed); DEN converted to kg m-3'
txt = json.dumps(idx, ensure_ascii=False, separators=(',', ':')); assert 'zeyangfeng' not in txt and '/glade' not in txt
open(f'{D}/index.json', 'w', encoding='utf-8').write(txt)
print('configs', len(cfgs), 'files', n, 'MB %.1f' % (size / 1e6))
