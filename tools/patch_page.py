import sys
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    c=s.count(a); assert c==n,(a[:70],c); s=s.replace(a,b)
rep("'G1-D','G2-D','G3-D','H-Ap'];\nvar CFG","'G1-D','G2-D','G3-D','H-Ap','N-D','N1-D','N-N1','N1-Ap'];\nvar CFG")
rep("I3:'2.0 + filter fix'};","I3:'2.0 + filter fix',N:'3.0.1 + NCAR settings',N1:'3.0.1 + DUFF'};")
rep("'H-Ap':'2.0, helium in mean molecular mass'};","'H-Ap':'2.0, helium in mean molecular mass',\n  'N-D':'full NCAR settings − 3.0.1','N1-D':'DUFF on − off','N-N1':'full NCAR settings − DUFF only','N1-Ap':'3.0.1 + DUFF − 2.0'};")
rep("note:'G1, G2, G3 each change one thing in 3.0.1; H changes one thing in 2.0.'}];","note:'G1, G2, G3 each change one thing in 3.0.1; H changes one thing in 2.0.'},\n  {id:'ncar',name:'NCAR settings',pairs:['N-D','N1-D','N-N1','N1-Ap'],eq:'N−D = (N−N1) + (N1−D)',\n   note:'N is 3.0.1 with the full NCAR recommended settings; N1 is 3.0.1 with only DUFF turned on. Temperature and hmF2 add exactly; percentages only approximately.'}];")
rep("var MAPF_CN={TN:'temperature',DEN:'density',NE:'electron density'};","var MAPF_CN={TN:'temperature',DEN:'density',NE:'electron density',hmF2:'hmF2',NmF2:'NmF2'};")
rep("O_N2:'O_N2'};\nfunction unitOf(f){ return f==='TN'?'K':((f==='UN'||f==='VN')?'m/s':'%'); }","O_N2:'O_N2',hmF2:'hmF2 F-layer peak height',NmF2:'NmF2 F-layer peak electron density'};\nfunction unitOf(f){ return f==='TN'?'K':((f==='UN'||f==='VN')?'m/s':(f==='hmF2'?'km':'%')); }\nfunction is2D(f){ return f==='hmF2'||f==='NmF2'; }\nfunction hkOf(f,km){ return is2D(f)?0:KMS.indexOf(km); }\nfunction kmTag(f,km){ return is2D(f)?'':km+' km · '; }")
rep("function mapLim(pair,field,km){ var st=(IDX.map_stats[field+'_'+km]||{})[pair];","function mapLim(pair,field,km){ var st=(IDX.map_stats[is2D(field)?field:field+'_'+km]||{})[pair];")
rep("if(c===255) return 'At least one member has no value at '+km+' km';","if(c===255) return 'At least one member has no value here';")
rep("var p=state.pair, fld=state.field, km=state.km, hk=KMS.indexOf(km), unit=unitOf(fld);","var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), unit=unitOf(fld);")
rep("km+' km · '+MAPF_CN[fld]+' difference · '+frameLabel(state.f)","kmTag(fld,km)+MAPF_CN[fld]+' difference · '+frameLabel(state.f)",s.count("km+' km · '+MAPF_CN[fld]+' difference · '+frameLabel(state.f)"))
rep("cellText(M,KMS.indexOf(state.km),state.f,","cellText(M,hkOf(state.field,state.km),state.f,")
rep("var p=state.pair, fld=state.field, km=state.km, hk=KMS.indexOf(km), f=state.f,","var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), f=state.f,")
rep("pairLabel(p)+' · '+km+' km · '+MAPF_CN[fld]+' difference'","pairLabel(p)+' · '+kmTag(fld,km)+MAPF_CN[fld]+' difference'")
rep("var fld=state.field, km=state.km, hk=KMS.indexOf(km), unit=unitOf(fld), zi=KMH.indexOf(km), limU=0;","var fld=state.field, km=state.km, hk=hkOf(fld,km), unit=unitOf(fld), zi=KMH.indexOf(km), limU=0;")
rep("var A=htArrays(Hd,fld,'dom'), lo=0, hi=0, f, k, X=function(f){ return qL+(FH[f]+0.5)/97*qw; };","var A=htArrays(Hd,fld,'dom'), lo=0, hi=0, f, k, X=function(f){ return qL+(FH[f]+0.5)/97*qw; };\n    if(!A.m){ text(c2,'No global-mean series for '+MAPF_CN[fld],qL,2,{base:'top',font:'11px '+UI,color:TOK.ink2}); return; }")
rep("['Code issues',['G1-D','G2-D','G3-D','H-Ap']]]","['Code issues',['G1-D','G2-D','G3-D','H-Ap']],['NCAR settings',['N-D','N1-D','N-N1','N1-Ap']]]")
rep("if(IDX.ht_fields.indexOf(f)>=0){ state.htField=f; htFieldSel.value=f; } renderAll('field'); }); fs.appendChild(b); });","if(IDX.ht_fields.indexOf(f)>=0){ state.htField=f; htFieldSel.value=f; } syncZ(); renderAll('field'); }); fs.appendChild(b); });")
rep("b.addEventListener('click',function(){ state.km=z; pressOnly(zs,b); renderAll('z'); }); zs.appendChild(b); });","b.addEventListener('click',function(){ state.km=z; pressOnly(zs,b); renderAll('z'); }); zs.appendChild(b); });\n  function syncZ(){ var two=is2D(state.field); Array.prototype.forEach.call(zs.children,function(b){ b.disabled=two; }); $('field2dNote').hidden=!two; }\n  syncZ();")
rep("subscribe:function(f){ subs.push(f); }, MAPF_CN:MAPF_CN };","subscribe:function(f){ subs.push(f); }, MAPF_CN:MAPF_CN, is2D:is2D };")
rep(".seg button:hover{ background:var(--accent-soft); }",".seg button:hover{ background:var(--accent-soft); }\n.seg button:disabled{ opacity:.4; cursor:default; background:var(--surface); }")
rep("""<label class="tog"><input type="checkbox" id="optHatch" checked> Hatch where values are missing</label>
    </div>
  </div>""","""<label class="tog"><input type="checkbox" id="optHatch" checked> Hatch where values are missing</label>
    </div>
  </div>
  <p id="field2dNote" hidden style="margin:12px 0 0;font-size:13.5px;line-height:1.45">hmF2 and NmF2 are the height and the electron density of the largest Ne in each model column, over the whole column, on the model’s own levels without interpolation, computed member by member. Where the F layer is weak the largest Ne can sit in the lower ionosphere, so hmF2 can jump by a few hundred km. The hmF2 difference is in km; the NmF2 difference is in % of the reference. They have no height, so the height buttons do not apply.</p>""")
rep("""<p class="msg" id="plot3dMsg" hidden>""","""<p class="msg" id="plot3dNote" hidden>hmF2 and NmF2 have one value per column, so there is nothing to stack by height here. Choose temperature, density or electron density for this view.</p>
      <p class="msg" id="plot3dMsg" hidden>""")
rep("function layers(){ var s=D.state, A=D.axes(), M=D.mapsFor(s.pair,s.field); if(!M || M.error) return null;","function layers(){ var s=D.state, A=D.axes(), M=D.mapsFor(s.pair,s.field); if(!M || M.error || M.codes.length<A.KMS.length) return null;")
rep("""function update(reason){
  if(!built){""","""var noteOn=false;
function showNote(on){ if(on===noteOn) return; noteOn=on; el.style.display=on?'none':''; document.getElementById('plot3dNote').hidden=!on; if(!on && built){ try{ Plotly.Plots.resize(el); }catch(_){} } }
function update(reason){
  if(D.axes().ready && D.is2D(D.state.field)){ showNote(true); lastKey=''; return; }
  showNote(false);
  if(!built){""")
open(dst,'w',encoding='utf-8').write(s); print('patched',len(s))
