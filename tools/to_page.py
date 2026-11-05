#!/usr/bin/env python3
"""Turn the 11/4 web re-export (npz) into the JSON the page reads. Old 14 pairs' TN/DEN/NE/ht files are copied unchanged;
the conversion itself is first tested by rebuilding one old pair and comparing the decoded bytes with the published file."""
import base64, gzip, json, os, re, shutil, sys
import numpy as np
E, OLD, OUT = sys.argv[1:4]
old = json.load(open(f'{OLD}/index.json', encoding='utf-8'))
oldpairs = [p['id'] for p in old['pairs']]; NEW = ['N-D', 'N1-D', 'N-N1', 'N1-Ap']; XY = {'N-D': ('N', 'D'), 'N1-D': ('N1', 'D'), 'N-N1': ('N', 'N1'), 'N1-Ap': ('N1', 'Ap')}
def pack(raw): return base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode()
def delta(u, C=144):
    a = u.reshape(-1, C).copy(); a[:, 1:] = (a[:, 1:].astype(int) - a[:, :-1].astype(int)) & 255; return a.astype(np.uint8).tobytes()
tmpl = json.load(open(f'{OLD}/maps_TN_D-C.json', encoding='utf-8')); ttmpl = json.load(open(f'{OLD}/ht_D-C.json', encoding='utf-8'))
def maps_json(pair, field):
    z = np.load(f'{E}/maps_{field}_{pair}.npz', allow_pickle=False)
    keys = [field] if field in ('hmF2', 'NmF2') else [f'{field}_{k}' for k in old['km_maps']]
    u = np.concatenate([z[k].ravel() for k in keys] + [z[k + '_same'].ravel() for k in keys])
    return {'pair': pair, 'field': field, 'shape': list(z[keys[0]].shape), 'km': ['peak'] if len(keys) == 1 else list(old['km_maps']), 'scale': [float(z[k + '_scale']) for k in keys],
            'order': tmpl['order'], 'encoding': tmpl['encoding'], 'b64': pack(delta(u))}
def ht_json(pair):
    z = np.load(f'{E}/ht_{pair}.npz', allow_pickle=False)
    raw = b''.join(np.asarray(z[f'{f}_{s}'], dtype='<f4').tobytes() for f in ttmpl['fields'] for s in ttmpl['stats'])
    return {'pair': pair, 'shape': list(z[f"{ttmpl['fields'][0]}_{ttmpl['stats'][0]}"].shape), 'fields': ttmpl['fields'], 'stats': ttmpl['stats'], 'order': ttmpl['order'], 'encoding': ttmpl['encoding'],
            'time_source': [int(x) for x in z['time_source']], 'b64': pack(raw)}
un = lambda s: gzip.decompress(base64.b64decode(s))
# test on an old pair
for name, new in ((f'maps_TN_D-C.json', maps_json('D-C', 'TN')), ('ht_D-C.json', ht_json('D-C'))):
    o = json.load(open(f'{OLD}/{name}', encoding='utf-8'))
    assert un(o['b64']) == un(new['b64']), name
    for k in o:
        if k != 'b64': assert o[k] == new[k], (name, k, o[k], new[k])
print('conversion test on D-C: decoded bytes and metadata identical to the published files')
def write(name, obj): json.dump(obj, open(f'{OUT}/{name}', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for n in os.listdir(OLD):
    if n != 'index.json': shutil.copy2(f'{OLD}/{n}', f'{OUT}/{n}')
def stat(pair, field, key):
    z = np.load(f'{E}/maps_{field}_{pair}.npz', allow_pickle=False); c = z[key]; s = float(z[key + '_scale']); v = np.abs((c[c != 255].astype(float) - 127) * s)
    return {'s': s, 'p999': s * 127, 'max_abs_encoded': float(v.max()), 'p99': float(np.percentile(v, 99)), 'n_points': int(c.size), 'n_nodata': int((c == 255).sum()), 'n_saturated': int(((c == 0) | (c == 254)).sum())}
idx = json.loads(json.dumps(old))
for p in NEW:
    for f in ('TN', 'DEN', 'NE'): write(f'maps_{f}_{p}.json', maps_json(p, f))
    h = ht_json(p); write(f'ht_{p}.json', h)
    idx['pairs'].append({'id': p, 'X': XY[p][0], 'Y': XY[p][1], 'maps': {f: f'maps_{f}_{p}.json' for f in ('DEN', 'NE', 'TN')}, 'ht': f'ht_{p}.json', 'ht_time_source': h['time_source']})
    for f in ('TN', 'DEN', 'NE'):
        for k in old['km_maps']: idx['map_stats'][f'{f}_{k}'][p] = stat(p, f, f'{f}_{k}')
for f in ('hmF2', 'NmF2'):
    idx['map_stats'][f] = {}
    for P in idx['pairs']:
        write(f'maps_{f}_{P["id"]}.json', maps_json(P['id'], f)); P['maps'][f] = f'maps_{f}_{P["id"]}.json'; idx['map_stats'][f][P['id']] = stat(P['id'], f, f)
idx['map_fields'] = ['TN', 'DEN', 'NE', 'hmF2', 'NmF2']
idx['units'].update({'hmF2': 'km (X-Y)', 'NmF2': '% of Y (pointwise 100 (X-Y)/Y)'})
idx['configs'].update({'N': '3.0.1 + NCAR settings', 'N1': '3.0.1 + DUFF'})
k = json.load(open(f'{E}/kp_grace.json', encoding='utf-8'))
assert k['kp']['kp'] == old['kp']['kp'] and k['grace_orbit_means']['obs'] == old['grace']['obs'] and k['grace_orbit_means']['time_utc'] == old['grace']['time_utc']
for c, v in old['grace']['model'].items(): assert k['grace_orbit_means']['model'][c] == v, c
idx['grace']['model'] = k['grace_orbit_means']['model']; print('grace configs', len(idx['grace']['model']), 'missing', old['grace'].get('missing_configs'))
idx['grace']['missing_configs'] = [c for c in old['grace'].get('missing_configs', []) if c not in idx['grace']['model']]
idx['source']['update'] = 'Re-export of 2026-11-04: adds comparisons N-D, N1-D, N-N1, N1-Ap and the quantities hmF2, NmF2 (peak of NE on model levels in each column, member by member) for all 18 comparisons. The original 14 comparisons are unchanged.'
txt = json.dumps(idx, ensure_ascii=False, separators=(',', ':'))
txt, n = re.subn(r'/glade/[^\s"\']*', lambda m: m.group(0).rstrip('/').rsplit('/', 1)[-1], txt); print('paths shortened', n)
assert 'zeyangfeng' not in txt and 'ndietrich' not in txt
open(f'{OUT}/index.json', 'w', encoding='utf-8').write(txt)
print('files', len(os.listdir(OUT)), 'MB', round(sum(os.path.getsize(f'{OUT}/{n}') for n in os.listdir(OUT)) / 1e6, 1), 'largest MB', round(max(os.path.getsize(f'{OUT}/{n}') for n in os.listdir(OUT)) / 1e6, 2))
for f in ('hmF2', 'NmF2'): print(f, {p: (round(idx['map_stats'][f][p]['p99'], 2), idx['map_stats'][f][p]['n_saturated']) for p in ('D-C', 'N1-D', 'N-D', 'N-N1')})
