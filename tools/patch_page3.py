import sys,re
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:80],s.count(a)); s=s.replace(a,b)
# ---- assimilation-minus-control pairs
rep("'G1-D','G2-D','G3-D','H-Ap','N-D','N1-D','N-N1','N1-Ap'];\nvar CFG","'G1-D','G2-D','G3-D','H-Ap','N-D','N1-D','N-N1','N1-Ap','exp6-ctrl95','v3exp1-v3ctrl','v3exp1_duff-v3ctrl_duff'];\nvar CFG")
rep("N:'3.0.1 + NCAR settings',N1:'3.0.1 + DUFF'};","N:'3.0.1 + NCAR settings',N1:'3.0.1 + DUFF',exp6:'2.0, assimilation (exp6)',ctrl95:'2.0, control (ctrl95)',v3exp1:'3.0.1 default, assimilation',v3ctrl:'3.0.1 default, control',v3exp1_duff:'3.0.1 + DUFF, assimilation',v3ctrl_duff:'3.0.1 + DUFF, control'};")
rep("'N-N1':'full NCAR settings − DUFF only','N1-Ap':'3.0.1 + DUFF − 2.0'};","'N-N1':'full NCAR settings − DUFF only','N1-Ap':'3.0.1 + DUFF − 2.0',\n  'exp6-ctrl95':'2.0: assimilation − control','v3exp1-v3ctrl':'3.0.1: assimilation − control','v3exp1_duff-v3ctrl_duff':'3.0.1 + DUFF: assimilation − control'};")
rep("note:'N is 3.0.1 with the full NCAR recommended settings; N1 is 3.0.1 with only DUFF turned on. Temperature and hmF2 add exactly; percentages only approximately.'}];",
    "note:'N is 3.0.1 with the full NCAR recommended settings; N1 is 3.0.1 with only DUFF turned on. Temperature and hmF2 add exactly; percentages only approximately.'},\n  {id:'assim',name:'Assimilation − control',pairs:['exp6-ctrl95','v3exp1-v3ctrl','v3exp1_duff-v3ctrl_duff'],eq:'',\n   note:'Each pair is an assimilation run minus its own control: the 1-hour forecast of each cycle, member i minus member i, then the 10-member mean. 7/5 00, 7/8 23 and 7/9 00 UT are not available for these pairs.'}];")
rep("['NCAR settings',['N-D','N1-D','N-N1','N1-Ap']]]","['NCAR settings',['N-D','N1-D','N-N1','N1-Ap']],['Assimilation − control',['exp6-ctrl95','v3exp1-v3ctrl','v3exp1_duff-v3ctrl_duff']]]")
# ---- experiments section reads figs/manifest.json
a=s.index("var EXPS=["); b=s.index("];",a)+2
s=s[:a]+"""var FIGORDER=['grace_validate_denPrior_timeseries','grace_validate_denPrior_dawndusk','grace_validate_ratio_metrics','diag_compare','diag_bias_alt','cosmic_bias_latlt','hmf2_cosmic','diag_overview','spread_check_timeseries','profile_spaghetti'];
var SETN={default:L('default','默认'),DUFF:'DUFF',NCAR:L('NCAR settings','NCAR 设置')};
function fmtStart(t){ var m=/^\\d{4}-(\\d\\d)-(\\d\\d)T(\\d\\d)/.exec(t||''); return m?(+m[1])+'/'+(+m[2])+' '+m[3]:(t||'?'); }
function entry(r){ var set=r.settings&&r.settings!=='default'?' + '+(SETN[r.settings]||r.settings):''; var kind=r.mode==='assim'?A:C;
  var label=(r.model||'?')+set+(r.members===90?L(', 90 members',', 90 成员'):'')+', '+kind;
  var m=[kind+', '+r.members+' '+M, ST+' '+fmtStart(r.start)+' UT, '+r.cycles+' '+CY]; if(r.control) m.push(CT+' '+r.control); if(r.dart) m.push('DART '+r.dart);
  var figs=FIGORDER.filter(function(f){ return (r.figures||[]).indexOf(f)>=0; }).concat((r.figures||[]).filter(function(f){ return FIGORDER.indexOf(f)<0; }));
  return {id:r.id,label:label,meta:m.join(' · '),figs:figs,key:[r.model||'',r.settings==='default'?0:(r.settings==='DUFF'?1:2),r.mode==='assim'?1:0,String(r.members||0).padStart(3,'0'),r.start||'',r.id].join('|')}; }
var EXPS=[];"""+s[b:]
rep("var FIG={\n  diag_overview:","var FIG={\n  grace_validate_ratio_metrics:{t:L('GRACE-FO density: ratio metrics','GRACE-FO 密度：比值指标'),c:L('Observed/model density ratio in the style of Bruinsma et al. (2021): mean of the ratio (exponential of the mean of ln), its standard deviation in percent, and Pearson R, for the whole window and each phase, control and assimilation forecast; the last rows after de-biasing with the quiet days.','按 Bruinsma 等（2021）的做法算的观测/模式密度比值：比值的平均（取对数平均再取指数）、它的标准差（百分数）和 Pearson 相关系数，全窗和各阶段，对照和同化预报；最后几行是用平静段去偏后的数。')},\n  cosmic_bias_latlt:{t:L('Where the Ne bias is: latitude and local time','Ne 偏差在哪里：纬度和地方时'),c:L('(model − obs)/obs in percent over the whole window, by latitude and local time, in three height bands, using every observation that has a forecast value (DART QC 0, 1, 2, 7). Right: GRACE-FO (ESA 0003) by latitude. Top row control, bottom row assimilation forecast.','全窗的（模式 − 观测）/观测，百分数，按纬度和地方时分格，三个高度带，用所有有预报值的观测（DART QC 0、1、2、7）。右侧是 GRACE-FO（ESA 0003）按纬度分。上排对照，下排同化预报。')},\n  hmf2_cosmic:{t:L('hmF2 against COSMIC-2','hmF2 对 COSMIC-2'),c:L('Top: mean hmF2 per cycle in the northern and southern hemispheres: COSMIC-2, control and assimilation forecasts. Bottom: whole-window mean of model − observed hmF2 by latitude and local time of the peak; cells with fewer than 30 profiles are blank.','上：南北半球每个循环的平均 hmF2，COSMIC-2、对照和同化预报。下：全窗的模式减观测 hmF2，按纬度和峰所在的地方时分格，不足 30 条剖面的格子留空。')},\n  diag_overview:")
rep("""EXPS.forEach(function(e){ var o=document.createElement('option'); o.value=e.id; o.textContent=e.label+' — '+e.id; sel.appendChild(o); });
var start='v3exp1_duff'; try{ var r=localStorage.getItem('tiegcm-exp'); if(r && EXPS.some(function(x){return x.id===r;})) start=r; }catch(_){}
sel.value=start; show(start); sel.addEventListener('change',function(){ show(sel.value); });""",
"""function figOf(f){ return FIG[f]||{t:f,c:''}; }
fetch(BASE+'figs/manifest.json').then(function(r){ if(!r.ok) throw new Error('manifest HTTP '+r.status); return r.json(); }).then(function(man){
  EXPS=(man.runs||[]).map(entry).sort(function(a,b){ return a.key<b.key?-1:(a.key>b.key?1:0); });
  EXPS.forEach(function(e){ var o=document.createElement('option'); o.value=e.id; o.textContent=e.label+' — '+e.id; sel.appendChild(o); });
  var start='v3exp1_duff'; try{ var r=localStorage.getItem('tiegcm-exp'); if(r && EXPS.some(function(x){return x.id===r;})) start=r; }catch(_){}
  if(!EXPS.some(function(x){return x.id===start;}) && EXPS.length) start=EXPS[EXPS.length-1].id;
  sel.value=start; show(start); window.TIEGCMFigs.exps=EXPS.map(function(e){return e.id;});
}).catch(function(e){ metaEl.textContent=L('The experiment list could not be loaded: ','实验清单没有读到：')+e.message; });
sel.addEventListener('change',function(){ show(sel.value); });""")
rep("grid.appendChild(card(BASE+'figs/runs/'+e.id+'/'+f+'.png',FIG[f].t,FIG[f].c,f==='grace_validate_denPrior_dawndusk'));","grid.appendChild(card(BASE+'figs/runs/'+e.id+'/'+f+'.png',figOf(f).t,figOf(f).c,f==='grace_validate_denPrior_dawndusk'||f==='grace_validate_ratio_metrics'||f==='cosmic_bias_latlt'));")
rep("<p>Every assimilation experiment produces the same seven figures when it finishes; control runs produce three.","<p>Every experiment produces the same set of figures when it finishes: ten for an assimilation run, six for a control run.")
rep('hmF2 and NmF2 are the height and the electron density of the largest Ne in each model column, over the whole column, on the model’s own levels without interpolation, computed member by member. Where the F layer is weak the largest Ne can sit in the lower ionosphere, so hmF2 can jump by a few hundred km. The hmF2 difference is in km; the NmF2 difference is in % of the reference. They have no height, so the height buttons do not apply.','hmF2 and NmF2 are the height and the electron density of the largest Ne in each model column, searched only over the levels at or above 200 km (so a strong E or F1 layer cannot be picked up as the peak), on the model’s own levels without interpolation, computed member by member. The hmF2 difference is in km; the NmF2 difference is in % of the reference. They have no height, so the height buttons do not apply.')
open(dst,'w',encoding='utf-8').write(s); print('patched3')
