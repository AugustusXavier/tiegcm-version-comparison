#!/usr/bin/env python3
"""Apply the 2026-11-06 re-export (web_export3) to data/full/: replace the hmF2/NmF2 maps of every pair
with the F-layer-restricted recompute, and add the three assimilation-minus-control pairs.
usage: python3 -I to_page3.py EXPORT3_DIR DATA_DIR"""
import base64, gzip, json, os, re, sys
import numpy as np
E, D = sys.argv[1:3]
idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
tmpl = json.load(open(f'{D}/maps_TN_D-C.json', encoding='utf-8')); ttmpl = json.load(open(f'{D}/ht_D-C.json', encoding='utf-8'))
pack = lambda raw: base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode()
def delta(u, C=144):
    a = u.reshape(-1, C).copy(); a[:, 1:] = (a[:, 1:].astype(int) - a[:, :-1].astype(int)) & 255; return a.astype(np.uint8).tobytes()
def maps_json(pair, field):
    z = np.load(f'{E}/maps_{field}_{pair}.npz', allow_pickle=False)
    keys = [field] if field in ('hmF2', 'NmF2') else [f'{field}_{k}' for k in idx['km_maps']]
    u = np.concatenate([z[k].ravel() for k in keys] + [z[k + '_same'].ravel() for k in keys])
    return {'pair': pair, 'field': field, 'shape': list(z[keys[0]].shape), 'km': ['peak'] if len(keys) == 1 else list(idx['km_maps']), 'scale': [float(z[k + '_scale']) for k in keys],
            'order': tmpl['order'], 'encoding': tmpl['encoding'], 'b64': pack(delta(u))}
def ht_json(pair):
    z = np.load(f'{E}/ht_{pair}.npz', allow_pickle=False)
    raw = b''.join(np.asarray(z[f'{f}_{s}'], dtype='<f4').tobytes() for f in ttmpl['fields'] for s in ttmpl['stats'])
    return {'pair': pair, 'shape': list(z[f"{ttmpl['fields'][0]}_{ttmpl['stats'][0]}"].shape), 'fields': ttmpl['fields'], 'stats': ttmpl['stats'], 'order': ttmpl['order'], 'encoding': ttmpl['encoding'],
            'time_source': [int(x) for x in z['time_source']], 'b64': pack(raw)}
def stat(pair, field, key):
    z = np.load(f'{E}/maps_{field}_{pair}.npz', allow_pickle=False); c = z[key]; s = float(z[key + '_scale']); v = np.abs((c[c != 255].astype(float) - 127) * s)
    return {'s': s, 'p999': s * 127, 'max_abs_encoded': float(v.max()) if v.size else 0.0, 'p99': float(np.percentile(v, 99)) if v.size else 0.0, 'n_points': int(c.size), 'n_nodata': int((c == 255).sum()), 'n_saturated': int(((c == 0) | (c == 254)).sum())}
def write(name, obj): json.dump(obj, open(f'{D}/{name}', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
old_ids = [p['id'] for p in idx['pairs']]
for p in old_ids:                       # 1. peaks recomputed for the existing pairs
    for f in ('hmF2', 'NmF2'): write(f'maps_{f}_{p}.json', maps_json(p, f)); idx['map_stats'][f][p] = stat(p, f, f)
NEW = {'exp6-ctrl95': ('exp6', 'ctrl95'), 'v3exp1-v3ctrl': ('v3exp1', 'v3ctrl'), 'v3exp1_duff-v3ctrl_duff': ('v3exp1_duff', 'v3ctrl_duff')}
for p, (x, y) in NEW.items():           # 2. assimilation minus control
    if p in old_ids: continue
    for f in ('TN', 'DEN', 'NE', 'hmF2', 'NmF2'): write(f'maps_{f}_{p}.json', maps_json(p, f))
    h = ht_json(p); write(f'ht_{p}.json', h)
    idx['pairs'].append({'id': p, 'X': x, 'Y': y, 'maps': {f: f'maps_{f}_{p}.json' for f in ('DEN', 'NE', 'TN', 'hmF2', 'NmF2')}, 'ht': f'ht_{p}.json', 'ht_time_source': h['time_source']})
    for f in ('TN', 'DEN', 'NE'):
        for k in idx['km_maps']: idx['map_stats'][f'{f}_{k}'][p] = stat(p, f, f'{f}_{k}')
    for f in ('hmF2', 'NmF2'): idx['map_stats'][f][p] = stat(p, f, f)
idx['configs'].update({'exp6': '2.0, assimilation (exp6)', 'ctrl95': '2.0, control (ctrl95)', 'v3exp1': '3.0.1 default, assimilation', 'v3ctrl': '3.0.1 default, control', 'v3exp1_duff': '3.0.1 + DUFF, assimilation', 'v3ctrl_duff': '3.0.1 + DUFF, control'})
idx['peak_definition'] = 'hmF2/NmF2 (re-export of 2026-11-06): per member and column, the largest Ne over the model levels with geometric height >= 200 km; no HMF2/NMF2 field of the files is used.'
idx['source']['update3'] = 'Re-export of 2026-11-06: hmF2/NmF2 recomputed with the search limited to levels at or above 200 km (all pairs); assimilation-minus-control pairs exp6-ctrl95, v3exp1-v3ctrl, v3exp1_duff-v3ctrl_duff added (1-hour forecasts, members matched one to one; 7/5 00, 7/8 23 and 7/9 00 UT not available).'
txt = json.dumps(idx, ensure_ascii=False, separators=(',', ':'))
txt, n = re.subn(r'/glade/[^\s"\']*', lambda m: m.group(0).rstrip('/').rsplit('/', 1)[-1], txt); assert 'zeyangfeng' not in txt
open(f'{D}/index.json', 'w', encoding='utf-8').write(txt)
print('pairs', len(idx['pairs']), 'paths shortened', n, 'files', len(os.listdir(D)), 'MB', round(sum(os.path.getsize(f'{D}/{x}') for x in os.listdir(D)) / 1e6, 1))
print('hmF2 saturation N-D before/after: see stats', {p: idx['map_stats']['hmF2'][p]['n_saturated'] for p in ('N-D', 'N-N1', 'exp6-ctrl95')})
