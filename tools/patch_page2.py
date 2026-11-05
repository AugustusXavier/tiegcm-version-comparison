import sys
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:80],s.count(a)); s=s.replace(a,b)
# ---- styles
rep(".foot{ font-size:13px;",""".topbar{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.lang{ font:400 13px/1.4 var(--font-ui); color:var(--accent); text-decoration:none; border:1px solid var(--line); border-radius:4px; padding:4px 10px; white-space:nowrap; }
.lang:hover{ background:var(--accent-soft); }
.toc{ display:flex; flex-wrap:wrap; gap:6px 16px; font-size:13px; margin-top:2px; }
.toc a{ color:var(--accent); text-decoration:none; border-bottom:1px solid transparent; } .toc a:hover{ border-bottom-color:var(--accent); }
.figgrid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(400px,1fr)); gap:16px; }
@media (max-width:560px){ .figgrid{ grid-template-columns:1fr; } }
.figcard{ background:var(--surface); border:1px solid var(--line); border-radius:2px; padding:10px 12px 12px; display:flex; flex-direction:column; gap:6px; min-width:0; }
.figcard img{ width:100%; height:auto; display:block; cursor:zoom-in; background:#fff; }
.figcard h3{ font-size:14.5px; font-weight:600; }
.figcard p{ font-size:13px; color:var(--ink-2); line-height:1.45; }
.expmeta{ font-size:13.5px; color:var(--ink-2); }
.lightbox{ position:fixed; inset:0; background:rgba(20,20,20,.86); display:none; align-items:center; justify-content:center; z-index:50; padding:24px; cursor:zoom-out; }
.lightbox.on{ display:flex; } .lightbox img{ max-width:100%; max-height:92vh; background:#fff; }
.foot{ font-size:13px;""")
# ---- header: language link, scope note, table of contents
rep("""  <header class="head">
    <p class="eyebrow">fixcmp1016 · 10-member mean</p>""","""  <header class="head">
    <div class="topbar"><p class="eyebrow">fixcmp1016 · 10-member mean</p><a class="lang" id="langLink" href="zh/" lang="zh">中文版</a></div>""")
rep("""    <p class="note" id="dataNote">Loading data…</p>
  </header>""","""    <p class="note" id="scopeNote"><b>Scope.</b> The maps and curves in the first five sections show differences between configurations only; they do not show which configuration is closer to the observations. Comparisons with observations are in the GRACE-FO section and in the two sections at the end.</p>
    <p class="note" id="dataNote">Loading data…</p>
    <nav class="toc" aria-label="Sections"><a href="#vA">Latitude–local time map</a><a href="#vB">Globe</a><a href="#vC">Height–time</a><a href="#vD">Groups</a><a href="#vE">3D layers</a><a href="#vF">GRACE-FO orbit means</a><a href="#vG">Experiments</a><a href="#vH">COSMIC-2</a></nav>
  </header>""")
# ---- new sections
rep("""  <footer class="foot" id="foot"></footer>""","""  <section class="view" id="vG" data-view="G">
    <div class="vhead">
      <h2>Experiments: fixed figures against observations</h2>
      <p>Every assimilation experiment produces the same seven figures when it finishes; control runs produce three. They compare the 1-hour forecast (and, for assimilation runs, the analysis) with the COSMIC-2 electron density and with the GRACE-FO density. The figures are made on the computing system from the run's own output and copied here unchanged. Click a figure to enlarge it.</p>
    </div>
    <div class="vctl row"><span class="lbl">Experiment</span><select class="sel" id="expSel" aria-label="Experiment"></select><span class="expmeta" id="expMeta"></span></div>
    <div class="figgrid" id="expFigs"></div>
  </section>

  <section class="view" id="vH" data-view="H">
    <div class="vhead">
      <h2>Model-only configurations against COSMIC-2</h2>
      <p>Seven configurations of the version comparison, run without assimilation, compared with the COSMIC-2 electron density profiles of the same four days: electron density by height band, and the F-layer peak height hmF2 (height of the largest Ne on each profile between 160 and 500 km, found the same way for observation and model). All configurations use the same 490,076 observations: levels not flagged bad in the ionPrf files and with a model value in every run; no DART outlier rejection. Drawn from the tables of the 11/3 computation.</p>
    </div>
    <div class="figgrid" id="cosmicFigs"></div>
  </section>

  <footer class="foot" id="foot"></footer>""")
# ---- script for the two sections and the lightbox
rep("""</body>""","""<div class="lightbox" id="lightbox" role="dialog" aria-label="Enlarged figure"><img id="lightboxImg" alt=""></div>
<script>
(function(){
'use strict';
var ZH=document.documentElement.lang==='zh', BASE=ZH?'../':'';
function L(en,zh){ return ZH?zh:en; }
var FIG={
  diag_overview:{t:L('Assimilation overview','同化总览'),c:L('Top left: forecast and analysis RMSE against the ensemble spread, per cycle. Top right: rank histogram, where each observation falls among the 10 members, all cycles. Bottom left: DART quality-control counts per cycle. Bottom right: observation minus forecast mean at the last cycle.','左上：每个循环的预报和分析 RMSE 对集合 spread。右上：秩直方图，每条观测落在 10 个成员中的第几位，全部循环。左下：每个循环 DART 质量控制的计数。右下：最后一个循环的观测减预报平均。')},
  diag_bias_alt:{t:L('Ne: bias and RMSE by height','Ne：偏差和分高度 RMSE'),c:L('Top: observation minus model electron density per cycle, forecast and analysis; positive means the model is below the observations. Bottom: forecast RMSE in three height bands.','上：每个循环的观测减模式电子密度，预报和分析；正值表示模式低于观测。下：三个高度带的预报 RMSE。')},
  diag_compare:{t:L('Ne: against the control','Ne：对对照运行'),c:L('Top: forecast electron density RMSE per cycle for the control, the forecast and the analysis, on the observations accepted by both runs. Bottom: improvement over the control in percent.','上：对照、预报、分析三者每个循环的电子密度 RMSE，用两个运行都接收的观测。下：相对对照的改善百分比。')},
  profile_spaghetti:{t:L('One profile, all members','一条剖面，全部成员'),c:L('One COSMIC-2 profile in the first cycle: the forecast members, their mean and the observation.','第一个循环里的一条 COSMIC-2 剖面：各预报成员、成员平均和观测。')},
  grace_validate_denPrior_timeseries:{t:L('GRACE-FO density: time series','GRACE-FO 密度：时间序列'),c:L('Top: GRACE-FO along-track density (raw and hourly means), with the control and assimilation 1-hour forecasts sampled at the same points. Bottom: relative difference to the observations in percent.','上：GRACE-FO 沿轨道的密度（原始值和每小时平均），以及在同样位置取值的对照和同化的一小时预报。下：相对观测的差，百分比。')},
  grace_validate_denPrior_dawndusk:{t:L('GRACE-FO density: dawn and dusk sides','GRACE-FO 密度：上午侧和傍晚侧'),c:L('The same comparison split by local solar time: dawn side (LST < 12) and dusk side (LST ≥ 12). R² is computed from 7/7 on.','同一比较按地方时分开：上午侧（地方时 < 12）和傍晚侧（≥ 12）。R² 从 7/7 起算。')},
  spread_check_timeseries:{t:L('Ensemble spread','集合 spread'),c:L('Spread of density at 500 km (top, % of the mean) and of temperature at 400 km (bottom, K): assimilation forecast, analysis and control.','500 km 密度的 spread（上，占平均的百分比）和 400 km 温度的 spread（下，K）：同化的预报、分析和对照。')}
};
var ASSIM=['grace_validate_denPrior_timeseries','grace_validate_denPrior_dawndusk','diag_compare','diag_bias_alt','diag_overview','spread_check_timeseries','profile_spaghetti'];
var CTRL=['diag_bias_alt','diag_overview','profile_spaghetti'];
var A=L('assimilation','同化'), C=L('control','对照'), M=L('members','成员'), CY=L('cycles','循环'), ST=L('start','起点'), CT=L('control run','对照运行');
function meta(kind,mem,start,n,ctrl,extra){ var p=[(kind==='assim'?A:C)+', '+mem+' '+M, ST+' '+start+' UT, '+n+' '+CY]; if(ctrl) p.push(CT+' '+ctrl); if(extra) p.push(extra); return p.join(' · '); }
var EXPS=[
  {id:'exp6',label:L('2.0, 10 members, full window','2.0，10 成员，全窗'),meta:meta('assim',10,'7/5 00',95,'ctrl95',L('DART v10.3.0','DART v10.3.0')),figs:ASSIM},
  {id:'exp8',label:L('2.0, 10 members, from storm onset','2.0，10 成员，从磁暴开始'),meta:meta('assim',10,'7/7 00',47,'ctrl95'),figs:ASSIM},
  {id:'exp9_a',label:L('2.0, 90 members, quiet days','2.0，90 成员，平静段'),meta:meta('assim',90,'7/5 00',48,'ctrl95_m90_a'),figs:ASSIM},
  {id:'exp9_b',label:L('2.0, 90 members, storm days','2.0，90 成员，磁暴段'),meta:meta('assim',90,'7/7 00',47,'ctrl95_m90_b'),figs:ASSIM},
  {id:'ctrl95_m90_a',label:L('2.0, 90 members, control, quiet days','2.0，90 成员，对照，平静段'),meta:meta('control',90,'7/5 00',48),figs:CTRL},
  {id:'ctrl95_m90_b',label:L('2.0, 90 members, control, storm days','2.0，90 成员，对照，磁暴段'),meta:meta('control',90,'7/7 00',47),figs:CTRL},
  {id:'v3ctrl',label:L('3.0.1 default, control','3.0.1 默认，对照'),meta:meta('control',10,'7/5 00',95),figs:CTRL},
  {id:'v3exp1',label:L('3.0.1 default, assimilation','3.0.1 默认，同化'),meta:meta('assim',10,'7/5 00',95,'v3ctrl',L('DART v10.3.0','DART v10.3.0')),figs:ASSIM},
  {id:'v3exp1_v11',label:L('3.0.1 default, DART v11.25.3, segment 1','3.0.1 默认，DART v11.25.3，第 1 段'),meta:meta('assim',10,'7/5 00',95,'v3ctrl',L('chain stopped early; continued by segments 2 and 3','链中途停止，由第 2、3 段接续')),figs:ASSIM},
  {id:'v3exp1_v11b',label:L('3.0.1 default, DART v11.25.3, segment 2','3.0.1 默认，DART v11.25.3，第 2 段'),meta:meta('assim',10,'7/7 00',47,'v3ctrl'),figs:ASSIM},
  {id:'v3exp1_v11c',label:L('3.0.1 default, DART v11.25.3, segment 3','3.0.1 默认，DART v11.25.3，第 3 段'),meta:meta('assim',10,'7/7 12',35,'v3ctrl'),figs:ASSIM},
  {id:'v3ctrl_duff',label:L('3.0.1 + DUFF, control','3.0.1 + DUFF，对照'),meta:meta('control',10,'7/5 00',95),figs:CTRL},
  {id:'v3exp1_duff',label:L('3.0.1 + DUFF, assimilation','3.0.1 + DUFF，同化'),meta:meta('assim',10,'7/5 00',95,'v3ctrl_duff',L('DART v11.25.3','DART v11.25.3')),figs:ASSIM}
];
var COSMIC=[
  {f:'cosmic2_Ne_seven_configs.png',t:L('Electron density by height band','分高度带的电子密度'),c:L('Mean Ne at the COSMIC-2 points in each 1-hour cycle, 3-hour running mean: observations and the seven configurations (10-member mean, 1-hour forecast). Whole-window bias and RMSE beside each panel.','每个 1 小时循环内 COSMIC-2 观测点上的平均 Ne，3 小时滑动平均：观测和七个配置（10 成员平均，一小时预报）。每格右侧是全窗的偏差和 RMSE。')},
  {f:'cosmic2_hmF2_seven_configs.png',t:L('F-layer peak height: time series','F 层峰高：时间序列'),c:L('Mean hmF2 of the profiles in each cycle, south and north of the equator, 3-hour running mean. Whole-window mean of model minus observation beside each panel.','每个循环内剖面的平均 hmF2，赤道以南和以北，3 小时滑动平均。每格右侧是全窗的模式减观测的平均。')},
  {f:'cosmic2_hmF2_maps_seven_configs.png',t:L('F-layer peak height: by latitude and local time','F 层峰高：按纬度和地方时'),c:L('Whole-window mean of model minus observation in 10° × 3-hour cells; cells with fewer than 30 profiles are blank. Last panel: DUFF on minus off.','全窗的模式减观测的平均，按 10° × 3 小时分格；不足 30 条剖面的格子留空。最后一格是开 DUFF 减不开。')}
];
var sel=document.getElementById('expSel'), metaEl=document.getElementById('expMeta'), grid=document.getElementById('expFigs'), cg=document.getElementById('cosmicFigs');
var lb=document.getElementById('lightbox'), lbi=document.getElementById('lightboxImg');
function card(src,t,c){ var d=document.createElement('div'); d.className='figcard'; var im=document.createElement('img'); im.loading='lazy'; im.src=src; im.alt=t; im.addEventListener('click',function(){ lbi.src=src; lbi.alt=t; lb.classList.add('on'); }); var h=document.createElement('h3'); h.textContent=t; var p=document.createElement('p'); p.textContent=c; d.appendChild(im); d.appendChild(h); d.appendChild(p); return d; }
function show(id){ var e=EXPS.filter(function(x){return x.id===id;})[0]; if(!e) return; metaEl.textContent=e.meta; grid.innerHTML=''; e.figs.forEach(function(f){ grid.appendChild(card(BASE+'figs/runs/'+e.id+'/'+f+'.png',FIG[f].t,FIG[f].c)); }); try{ localStorage.setItem('tiegcm-exp',id); }catch(_){} }
EXPS.forEach(function(e){ var o=document.createElement('option'); o.value=e.id; o.textContent=e.label+' — '+e.id; sel.appendChild(o); });
var start='v3exp1_duff'; try{ var r=localStorage.getItem('tiegcm-exp'); if(r && EXPS.some(function(x){return x.id===r;})) start=r; }catch(_){}
sel.value=start; show(start); sel.addEventListener('change',function(){ show(sel.value); });
COSMIC.forEach(function(x){ cg.appendChild(card(BASE+'figs/cosmic/'+x.f,x.t,x.c)); });
lb.addEventListener('click',function(){ lb.classList.remove('on'); lbi.src=''; });
document.addEventListener('keydown',function(ev){ if(ev.key==='Escape' && lb.classList.contains('on')){ lb.classList.remove('on'); lbi.src=''; } });
window.TIEGCMFigs={ exps:EXPS.map(function(e){return e.id;}), figs:Object.keys(FIG), cosmic:COSMIC.length };
})();
</script>
</body>""")
open(dst,'w',encoding='utf-8').write(s); print('patched2',len(s))
