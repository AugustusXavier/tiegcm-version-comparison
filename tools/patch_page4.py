#!/usr/bin/env python3
"""Add the 'show X / Y itself' view (2026-11-07): a Show segment in the time bar, one-hue colour scale, own-field loaders,
map/globe/height-time/3D branches that draw the field of one configuration instead of the difference.
usage: python3 -I patch_page4.py index.html index.html"""
import sys
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:90],s.count(a)); s=s.replace(a,b)
# ---- CSS tokens and legend swatch
rep("  --div-p1:#fddbc7; --div-p2:#f4a582; --div-p3:#d6604d; --div-p4:#b2182b; --div-p5:#67001f;\n",
    "  --div-p1:#fddbc7; --div-p2:#f4a582; --div-p3:#d6604d; --div-p4:#b2182b; --div-p5:#67001f;\n  --seq-1:#ffffcc; --seq-2:#ffeda0; --seq-3:#fed976; --seq-4:#feb24c; --seq-5:#fd8d3c; --seq-6:#fc4e2a; --seq-7:#e31a1c; --seq-8:#bd0026; --seq-9:#800026;\n")
rep(".sw-dot{ background:radial-gradient(circle,var(--ink) 1.4px,transparent 1.8px) 0 0/8px 8px, var(--div-mid); }",
    ".sw-seq{ background:linear-gradient(90deg,var(--seq-2),var(--seq-5),var(--seq-9)); }\n.sw-dot{ background:radial-gradient(circle,var(--ink) 1.4px,transparent 1.8px) 0 0/8px 8px, var(--div-mid); }")
# ---- header text
rep("The time bar controls all figures: press play to step hour by hour, drag the slider to change the time, and choose the comparison, quantity and height.</p>",
    "The time bar controls all figures: press play to step hour by hour, drag the slider to change the time, and choose the comparison, quantity and height. The buttons after the height choose what is drawn: the difference, or the field of one of the two configurations itself.</p>")
rep("      <li><span class=\"sw sw-dot\"></span>Small dots: fewer than 8 of the 10 members have the sign of the mean</li>",
    "      <li><span class=\"sw sw-seq\"></span>One-hue scale: the field itself, when one configuration is shown instead of the difference</li>\n      <li><span class=\"sw sw-dot\"></span>Small dots: fewer than 8 of the 10 members have the sign of the mean</li>")
# ---- time bar: Show segment
rep("""      <div class="seg" role="group" aria-label="Height" id="zSeg"></div>
      <label class="tog"><input type="checkbox" id="optDots" checked> Dots where members disagree</label>""",
"""      <div class="seg" role="group" aria-label="Height" id="zSeg"></div>
      <span class="lbl">Show</span>
      <div class="seg" role="group" aria-label="Show the difference or one configuration" id="showSeg"><button type="button" data-show="diff" aria-pressed="true">X − Y</button><button type="button" data-show="X" aria-pressed="false">X</button><button type="button" data-show="Y" aria-pressed="false">Y</button></div>
      <label class="tog"><input type="checkbox" id="optDots" checked> Dots where members disagree</label>""")
# ---- section texts
rep("<p>Horizontal axis: local time; vertical axis: latitude; color: the 10-member mean difference. Hover over a cell to see its value, its geographic longitude and how many members have the same sign.</p>",
    "<p>Horizontal axis: local time; vertical axis: latitude; color: the 10-member mean difference, or the 10-member mean of the field itself when one configuration is shown. Hover over a cell to see its value, its geographic longitude and how many members have the same sign.</p>")
rep("<p>Related comparisons side by side at the same time and height. Below each map: the global-mean difference of that comparison at this height against time; shading: member minimum to maximum; vertical line: current time.</p>",
    "<p>Related comparisons side by side at the same time and height. Below each map: the global-mean difference of that comparison at this height against time; shading: member minimum to maximum; vertical line: current time. This section always shows differences, whichever Show button is pressed.</p>")
rep("<p>Left: global-mean difference against height and time; the vertical line is the current time. Right: the profile at the current time. Click the left plot to jump to that time. These plots use the comparison chosen in the time bar; the quantity is chosen here.</p>",
    "<p>Left: global-mean difference against height and time; the vertical line is the current time. Right: the profile at the current time. Click the left plot to jump to that time. These plots use the comparison chosen in the time bar; the quantity is chosen here. When one configuration is shown, the plots give its global mean itself (logarithmic colours and axis for densities and mixing ratios).</p>")
# ---- state
rep("var state={f:0, playing:false, fps:5, pair:null, field:'TN', km:400, dots:true, hatch:true, unified:true, follow:false,",
    "var state={f:0, playing:false, fps:5, pair:null, field:'TN', km:400, dots:true, hatch:true, unified:true, follow:false, show:'diff',")
# ---- loaders for the fields themselves
rep("""/* ---------------- colour scale ---------------- */
var TOK={}, LUT=new Uint8ClampedArray(768);""",
"""/* ---------------- the fields themselves (one configuration instead of the difference) ---------------- */
var ownStore=new Map();
function ownFor(cfg,field){
  var key=cfg+'|'+field, rec=ownStore.get(key);
  if(rec) return rec.state==='ok'?rec.data:(rec.state==='err'?{error:rec.err}:undefined);
  var O=IDX.own&&IDX.own.configs[cfg]; if(!O || !O.maps || !O.maps[field]) return null;
  rec={state:'loading'}; ownStore.set(key,rec);
  getJSON(O.maps[field]).then(function(J){ return gunzip(b64bytes(J.b64)).then(function(u){
      var S=J.shape[0]*J.shape[1]*J.shape[2], nk=J.km.length, C=J.shape[2];
      if(J.shape[0]!==NT || J.shape[1]!==NLAT || C!==NLT) throw new Error(O.maps[field]+': shape does not match index');
      if(u.length!==nk*S) throw new Error(O.maps[field]+': wrong length after decompression');
      var rows=u.length/C;
      for(var r=0;r<rows;r++){ var o=r*C, acc=u[o]; for(var j=1;j<C;j++){ acc=(acc+u[o+j])&255; u[o+j]=acc; } }
      var codes=[]; for(var h=0;h<nk;h++) codes.push(u.subarray(h*S,(h+1)*S));
      rec.state='ok'; rec.data={codes:codes,lo:J.lo,s:J.scale,log:!!J.log,unit:J.unit||'',km:J.km,ts:J.time_source}; }); })
    .catch(function(e){ rec.state='err'; rec.err=String(e&&e.message||e); console.error(e); })
    .then(function(){ renderAll('data'); });
  return undefined;
}
var ownHtStore=new Map();
function ownHtFor(cfg){
  var rec=ownHtStore.get(cfg);
  if(rec) return rec.state==='ok'?rec.data:(rec.state==='err'?{error:rec.err}:undefined);
  var O=IDX.own&&IDX.own.configs[cfg]; if(!O || !O.ht) return null;
  rec={state:'loading'}; ownHtStore.set(cfg,rec);
  getJSON(O.ht).then(function(J){ return gunzip(b64bytes(J.b64)).then(function(u){
      var L=J.shape[0]*J.shape[1], nf=J.fields.length, ns=J.stats.length;
      if(J.shape[0]!==NT || J.shape[1]!==NK) throw new Error(O.ht+': shape does not match index');
      if(u.byteLength!==4*L*nf*ns) throw new Error(O.ht+': wrong length after decompression');
      var a=new Float32Array(u.buffer,u.byteOffset,L*nf*ns);
      rec.state='ok'; rec.data={ts:J.time_source,fields:J.fields,stats:J.stats,
        get:function(f,st){ var fi=J.fields.indexOf(f), si=J.stats.indexOf(st); if(fi<0||si<0) return null; var o=(fi*ns+si)*L; return a.subarray(o,o+L); }}; }); })
    .catch(function(e){ rec.state='err'; rec.err=String(e&&e.message||e); console.error(e); })
    .then(function(){ renderAll('data'); });
  return undefined;
}
function shownCfg(){ if(state.show==='diff' || !IDX || !IDX.own) return null; var xy=pairXY(state.pair); var c=state.show==='X'?xy[0]:xy[1]; return IDX.own.configs[c]?c:null; }
function isLogMap(f){ return !!(IDX && IDX.own && IDX.own.log.indexOf(f)>=0); }
var HT_LOG=['O2','N2','HE','NO','NO_COOL','OP','O_N2','NE','DEN'];
function isLogHt(f){ return HT_LOG.indexOf(f)>=0; }
function ownUnit(f){ if(!IDX||!IDX.own) return ''; var U=IDX.own; return (U.units&&U.units[f]!==undefined?U.units[f]:(U.ht_units&&U.ht_units[f]))||''; }
function tickStep(lo,hi,n){ var span=hi-lo; if(!(span>0)) return 1; var raw=span/n, e=Math.pow(10,Math.floor(Math.log10(raw))), f=raw/e; return (f<1.5?1:(f<3?2:(f<7?5:10)))*e; }
/* colour range for the field itself: the 1st to 99th percentile of X and of Y together (all times), so that the two can be compared by switching; values outside saturate */
function ownRange(field,km){ var key=is2D(field)?field:field+'_'+km, R=(IDX.own.range||{})[key]||{}, xy=pairXY(state.pair), lo=Infinity, hi=-Infinity;
  xy.forEach(function(c){ var r=R[c]; if(r){ var a=r.length>3?r[2]:r[0], b=r.length>3?r[3]:r[1]; if(a<lo) lo=a; if(b>hi) hi=b; } }); if(!(lo<hi)) return null;
  var lg=isLogMap(field); if(lg){ lo=Math.floor(lo*10)/10; hi=Math.ceil(hi*10)/10; } else { var st=tickStep(lo,hi,5)/2; lo=Math.floor(lo/st)*st; hi=Math.ceil(hi/st)*st; }
  return {lo:lo,hi:hi,log:lg}; }
var SUP={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
function sup(n){ return String(n).split('').map(function(c){ return SUP[c]||c; }).join(''); }
function sciText(v,sig){ if(!(v===v)) return '—'; if(v===0) return '0'; var e=Math.floor(Math.log10(Math.abs(v))), m=v/Math.pow(10,e), d=Math.max(0,(sig||3)-1), ms=m.toFixed(d); if(Math.abs(parseFloat(ms))>=10){ e+=1; ms=(m/10).toFixed(d); } return ms+'×10'+sup(e); }
function fmtLin(v,span){ var d=span>=20?0:(span>=2?1:2); return v.toFixed(d); }
function linTicks(lo,hi,n){ return niceTicks(lo,hi,n).map(function(v){ return {v:v,s:fmtLin(v,hi-lo)}; }); }
function logTicks(lo,hi,n){ var sets=[[1],[1,2,5],[1,2,3,5,7],[1,1.5,2,3,4,5,6,7,8,9]], best=null;
  sets.forEach(function(ms){ var out=[]; for(var k=Math.floor(lo)-1;k<=Math.ceil(hi);k++) ms.forEach(function(m){ var L=k+Math.log10(m); if(L>=lo-1e-9 && L<=hi+1e-9) out.push({v:L,s:(m===1?'10'+sup(k):String(m)+'×10'+sup(k))}); });
    if(out.length<=n+2 && (best===null || out.length>best.length)) best=out; });
  if(!best){ var dec=[]; for(var k=Math.ceil(lo);k<=Math.floor(hi);k++) dec.push({v:k,s:'10'+sup(k)}); var stride=Math.ceil(dec.length/(n+2)); best=dec.filter(function(t,i){ return i%stride===0; }); }
  return best; }

/* ---------------- colour scale ---------------- */
var TOK={}, LUT=new Uint8ClampedArray(768), LUTS=new Uint8ClampedArray(768);""")
rep("""  for(var i=0;i<256;i++){ var u=i/255*10, k=Math.min(9,Math.floor(u)), f=u-k, A=TOK.div[k], B=TOK.div[k+1];
    LUT[3*i]=A[0]+(B[0]-A[0])*f; LUT[3*i+1]=A[1]+(B[1]-A[1])*f; LUT[3*i+2]=A[2]+(B[2]-A[2])*f; }
}""",
"""  for(var i=0;i<256;i++){ var u=i/255*10, k=Math.min(9,Math.floor(u)), f=u-k, A=TOK.div[k], B=TOK.div[k+1];
    LUT[3*i]=A[0]+(B[0]-A[0])*f; LUT[3*i+1]=A[1]+(B[1]-A[1])*f; LUT[3*i+2]=A[2]+(B[2]-A[2])*f; }
  TOK.seq=['--seq-1','--seq-2','--seq-3','--seq-4','--seq-5','--seq-6','--seq-7','--seq-8','--seq-9'].map(function(n){ return hexRGB(g(n)); });
  for(var i2=0;i2<256;i2++){ var u2=i2/255*8, k2=Math.min(7,Math.floor(u2)), f2=u2-k2, A2=TOK.seq[k2], B2=TOK.seq[k2+1];
    LUTS[3*i2]=A2[0]+(B2[0]-A2[0])*f2; LUTS[3*i2+1]=A2[1]+(B2[1]-A2[1])*f2; LUTS[3*i2+2]=A2[2]+(B2[2]-A2[2])*f2; }
}
function sidx(v,R){ var u=(v-R.lo)/(R.hi-R.lo); if(u<0) u=0; else if(u>1) u=1; return Math.round(u*255); }""")
# ---- sequential colour bar
rep("""function msgBox(ctx,x,y,w,h,s){""",
"""function drawBarSeq(ctx,x,y,w,h,R,unit,small){
  for(var i=0;i<h;i++){ var u=1-i/(h-1), c=Math.round(u*255)*3; ctx.fillStyle='rgb('+LUTS[c]+','+LUTS[c+1]+','+LUTS[c+2]+')'; ctx.fillRect(x,y+i,w,1.5); }
  ctx.strokeStyle=TOK.axis; ctx.lineWidth=1; ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
  var fs=small?10:11, ticks=R.log?logTicks(R.lo,R.hi,small?3:6):linTicks(R.lo,R.hi,small?3:5);
  ticks.forEach(function(t){ var Y=y+(1-(t.v-R.lo)/(R.hi-R.lo))*(h-1); ctx.beginPath(); ctx.moveTo(x+w,Y); ctx.lineTo(x+w+3,Y); ctx.stroke(); text(ctx,t.s,x+w+5,Y,{base:'middle',font:fs+'px '+MONO}); });
  text(ctx,unit,x,y-6,{font:fs+'px '+MONO});
}
function msgBox(ctx,x,y,w,h,s){""")
# ---- painting: own fields through the same drawMap
rep("""  offx.putImageData(offImg,0,0); return off; }
function drawMap(ctx,x,y,w,h,M,hk,f,lim,o){
  ctx.imageSmoothingEnabled=false; ctx.drawImage(paintMap(M,hk,f,lim),x,y,w,h);
  var cw=w/NLT, ch=h/NLAT, codes=M.codes[hk], same=M.same[hk], base=f*N, i, j, k, r;""",
"""  offx.putImageData(offImg,0,0); return off; }
function paintOwn(O,hk,f,R){
  var d=offImg.data, codes=O.codes[hk], lo=O.lo[hk], s=O.s[hk], base=f*N, sr=TOK.surfRGB;
  for(var i=0;i<NLAT;i++){ var r=NLAT-1-i; for(var j=0;j<NLT;j++){ var c=codes[base+i*NLT+j], o=(r*NLT+j)*4;
    if(c===255){ d[o]=sr[0]; d[o+1]=sr[1]; d[o+2]=sr[2]; }
    else { var q=sidx(lo+c*s,R)*3; d[o]=LUTS[q]; d[o+1]=LUTS[q+1]; d[o+2]=LUTS[q+2]; }
    d[o+3]=255; } }
  offx.putImageData(offImg,0,0); return off; }
/* o.own: M is the field of one configuration (from ownFor) and lim is its colour range {lo,hi,log} */
function drawMap(ctx,x,y,w,h,M,hk,f,lim,o){
  o=o||{}; var own=!!o.own;
  ctx.imageSmoothingEnabled=false; ctx.drawImage(own?paintOwn(M,hk,f,lim):paintMap(M,hk,f,lim),x,y,w,h);
  var cw=w/NLT, ch=h/NLAT, codes=M.codes[hk], same=own?null:M.same[hk], base=f*N, i, j, k, r;""")
rep("""  if(state.dots){ var rad=Math.max(0.6,Math.min(cw,ch)*0.2);""","""  if(state.dots && same){ var rad=Math.max(0.6,Math.min(cw,ch)*0.2);""")
rep("""  return s+' · '+M.same[hk][k]+'/10 members with the same sign';
}""",
"""  return s+' · '+M.same[hk][k]+'/10 members with the same sign';
}
function ownCellText(O,hk,f,i,j){
  var k=f*N+i*NLT+j, c=O.codes[hk][k];
  if(c===255) return (O.ts && O.ts[f]<0) ? 'Not available at this time' : 'At least one member has no value here';
  var lv=O.lo[hk]+c*O.s[hk], s;
  if(O.log) s=sciText(Math.pow(10,lv),3); else { var dec=Math.max(0,Math.min(3,Math.ceil(-Math.log10(O.s[hk]/2)))); s=lv.toFixed(dec); }
  s+=' '+O.unit;
  if(c===0) s='≤ '+s+' (outside the encoding range)'; else if(c===254) s='≥ '+s+' (outside the encoding range)';
  return s;
}""")
# ---- view A
rep("""function renderA(){
  var W=figA.clientWidth-24, mL=44, mR=74, mB=40, pw=W-mL-mR, ph=Math.min(440,Math.max(150,pw/2)), TF='500 13px '+UI;
  pw=Math.min(pw,ph*2);
  var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), unit=unitOf(fld);
  var tl=IDX? splitTitle([titleLine(p), kmTag(fld,km)+MAPF_CN[fld]+' difference · '+frameLabel(state.f)],' · ',TF,Math.max(120,W-mL-8),[titleLine(p), km+' km · '+MAPF_CN[fld]+' difference · 7/8 23:00 UT · end of spin-up']) : [''];""",
"""function ownTitle(c){ return cfgShort(c)+'   '+(CFG[c]||''); }
function renderA(){
  var oc=shownCfg(), W=figA.clientWidth-24, mL=44, mR=oc?104:74, mB=40, pw=W-mL-mR, ph=Math.min(440,Math.max(150,pw/2)), TF='500 13px '+UI;
  pw=Math.min(pw,ph*2);
  var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), unit=unitOf(fld);
  var tl=IDX? (oc? splitTitle([ownTitle(oc), kmTag(fld,km)+MAPF_CN[fld]+' · '+frameLabel(state.f)],' · ',TF,Math.max(120,W-mL-8),[ownTitle(oc), km+' km · '+MAPF_CN[fld]+' · 7/8 23:00 UT · end of spin-up'])
    : splitTitle([titleLine(p), kmTag(fld,km)+MAPF_CN[fld]+' difference · '+frameLabel(state.f)],' · ',TF,Math.max(120,W-mL-8),[titleLine(p), km+' km · '+MAPF_CN[fld]+' difference · 7/8 23:00 UT · end of spin-up'])) : [''];""")
rep("""  tl.forEach(function(s,n){ text(ctx,s,mL,18+16*n,{font:TF,color:TOK.ink}); });
  var M=mapsFor(p,fld), m=stateMsg(M,MAPF_CN[fld]+' map'); if(m){ msgBox(ctx,mL,mT,pw,ph,m); return; }
  var lim=mapLim(p,fld,km);
  drawMap(ctx,mL,mT,pw,ph,M,hk,state.f,lim,{});""",
"""  tl.forEach(function(s,n){ text(ctx,s,mL,18+16*n,{font:TF,color:TOK.ink}); });
  if(oc){ var O=ownFor(oc,fld), mo=stateMsg(O,MAPF_CN[fld]+' map'); if(mo){ msgBox(ctx,mL,mT,pw,ph,mo); return; }
    var R=ownRange(fld,km); if(!R){ msgBox(ctx,mL,mT,pw,ph,'No colour range for this field'); return; }
    drawMap(ctx,mL,mT,pw,ph,O,hk,state.f,R,{own:true});
    text(ctx,'Local time (h)',mL+pw/2,mT+ph+22,{align:'center',base:'top',font:'11.5px '+UI,color:TOK.ink2});
    ctx.save(); ctx.translate(12,mT+ph/2); ctx.rotate(-Math.PI/2); text(ctx,'Latitude (°)',0,0,{align:'center',base:'middle',font:'11.5px '+UI,color:TOK.ink2}); ctx.restore();
    drawBarSeq(ctx,mL+pw+16,mT+10,12,ph-14,R,O.unit);
    rectA={x:mL+shift,y:mT,w:pw,h:ph}; return; }
  var M=mapsFor(p,fld), m=stateMsg(M,MAPF_CN[fld]+' map'); if(m){ msgBox(ctx,mL,mT,pw,ph,m); return; }
  var lim=mapLim(p,fld,km);
  drawMap(ctx,mL,mT,pw,ph,M,hk,state.f,lim,{});""")
rep("""  var M=mapsFor(state.pair,state.field); if(!M||M.error){ tipA.hidden=true; return; }
  var j=Math.min(NLT-1,Math.floor(x/rectA.w*NLT)), i=NLAT-1-Math.min(NLAT-1,Math.floor(y/rectA.h*NLAT));
  var L=LT[j], hh=Math.floor(L+1e-6), mm=Math.round((L-hh)*60)%60, lon=wrapLon(15*(L-UTH[state.f]));
  showTip(tipA,figA,e,['Lat '+LAT[i].toFixed(2)+'° · LT '+pad2(hh)+':'+pad2(mm)+' · Lon '+lonText(lon),
    cellText(M,hkOf(state.field,state.km),state.f,i,j,state.km,unitOf(state.field),mapLim(state.pair,state.field,state.km))]); });""",
"""  var oc=shownCfg(), M=oc?ownFor(oc,state.field):mapsFor(state.pair,state.field); if(!M||M.error){ tipA.hidden=true; return; }
  var j=Math.min(NLT-1,Math.floor(x/rectA.w*NLT)), i=NLAT-1-Math.min(NLAT-1,Math.floor(y/rectA.h*NLAT));
  var L=LT[j], hh=Math.floor(L+1e-6), mm=Math.round((L-hh)*60)%60, lon=wrapLon(15*(L-UTH[state.f]));
  showTip(tipA,figA,e,['Lat '+LAT[i].toFixed(2)+'° · LT '+pad2(hh)+':'+pad2(mm)+' · Lon '+lonText(lon),
    oc? ownCellText(M,hkOf(state.field,state.km),state.f,i,j) : cellText(M,hkOf(state.field,state.km),state.f,i,j,state.km,unitOf(state.field),mapLim(state.pair,state.field,state.km))]); });""")
# ---- view B: globe
rep("""  var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), f=state.f, unit=unitOf(fld), sLon=subsolarLon(f), DEC=declination(DOYS[f],UTH[f]);
  var M=mapsFor(p,fld), m=stateMsg(M,MAPF_CN[fld]+' map');
  gInfo.innerHTML='';
  if(m){ text(ctx,m,cx,cy,{align:'center',base:'middle',font:'13px '+UI,color:TOK.ink2}); return; }
  if(state.follow){ gYaw=sLon*D2R; }
  var lim=mapLim(p,fld,km), codes=M.codes[hk], s=M.s[hk], base=f*N, sr=TOK.surfRGB, hr=TOK.hatchRGB;
  if(!cellRGB || cellRGB.length!==N*3) cellRGB=new Uint8Array(N*3);
  for(var k0=0;k0<N;k0++){ var c0=codes[base+k0]; if(c0===255){ cellRGB[3*k0]=0; cellRGB[3*k0+1]=0; cellRGB[3*k0+2]=0; continue; }
    var q=cidx((c0-127)*s,lim)*3; cellRGB[3*k0]=LUT[q]; cellRGB[3*k0+1]=LUT[q+1]; cellRGB[3*k0+2]=LUT[q+2]; }""",
"""  var p=state.pair, fld=state.field, km=state.km, hk=hkOf(fld,km), f=state.f, unit=unitOf(fld), sLon=subsolarLon(f), DEC=declination(DOYS[f],UTH[f]), oc=shownCfg();
  var M=oc?ownFor(oc,fld):mapsFor(p,fld), m=stateMsg(M,MAPF_CN[fld]+' map'), OR=oc?ownRange(fld,km):null;
  gInfo.innerHTML='';
  if(!m && oc && !OR) m='No colour range for this field';
  if(m){ text(ctx,m,cx,cy,{align:'center',base:'middle',font:'13px '+UI,color:TOK.ink2}); return; }
  if(state.follow){ gYaw=sLon*D2R; }
  var lim=oc?0:mapLim(p,fld,km), codes=M.codes[hk], s=M.s[hk], olo=oc?M.lo[hk]:0, base=f*N, sr=TOK.surfRGB, hr=TOK.hatchRGB;
  if(!cellRGB || cellRGB.length!==N*3) cellRGB=new Uint8Array(N*3);
  for(var k0=0;k0<N;k0++){ var c0=codes[base+k0]; if(c0===255){ cellRGB[3*k0]=0; cellRGB[3*k0+1]=0; cellRGB[3*k0+2]=0; continue; }
    if(oc){ var q2=sidx(olo+c0*s,OR)*3; cellRGB[3*k0]=LUTS[q2]; cellRGB[3*k0+1]=LUTS[q2+1]; cellRGB[3*k0+2]=LUTS[q2+2]; continue; }
    var q=cidx((c0-127)*s,lim)*3; cellRGB[3*k0]=LUT[q]; cellRGB[3*k0+1]=LUT[q+1]; cellRGB[3*k0+2]=LUT[q+2]; }""")
rep("""  var bctx=fit(cBbar,150,220); drawBar(bctx,8,22,14,190,lim,unit);
  var lines=[pairLabel(p)+' · '+kmTag(fld,km)+MAPF_CN[fld]+' difference', 'Time '+frameLabel(f), 'Subsolar point '+DEC.toFixed(1)+'°N, '+lonText(sLon)];""",
"""  var bctx=fit(cBbar,150,220); if(oc) drawBarSeq(bctx,8,22,14,190,OR,M.unit); else drawBar(bctx,8,22,14,190,lim,unit);
  var lines=[oc? cfgShort(oc)+' · '+kmTag(fld,km)+MAPF_CN[fld] : pairLabel(p)+' · '+kmTag(fld,km)+MAPF_CN[fld]+' difference', 'Time '+frameLabel(f), 'Subsolar point '+DEC.toFixed(1)+'°N, '+lonText(sLon)];""")
# ---- view C: height-time
rep("""function renderC(){
  var wrap=cC1.parentNode, W1=wrap.clientWidth, mL=46, mR=64, mB=36, pw=W1-mL-mR, ph=Math.max(180,Math.min(340,pw*0.55)), TF='500 13px '+UI;
  var p=state.pair, fld=state.htField, stat=state.htStat, unit=unitOf(fld);
  var statName=stat==='dom'?'Global-mean difference':(unit==='%'?'Normalized typical difference':'Typical difference');
  var tl=IDX? splitTitle([pairLabel(p)+'   '+FIELD_CN[fld], statName+' ('+unit+')'],' · ',TF,Math.max(120,W1-mL-8)) : [''];
  var mT=tl.length>1?50:34;
  var ctx=fit(cC1,W1,ph+mT+mB); rectC=null;
  var W2=cC2.parentNode.clientWidth, H2=ph+mT+mB, c2=fit(cC2,W2,H2);
  if(!IDX) return;
  var Hd=htFor(p);
  tl.forEach(function(s,n){ text(ctx,s,mL,14+16*n,{font:TF,color:TOK.ink}); });""",
"""function ownHtArrays(Hd,fld){ return {m:Hd.get(fld,'mean'), lo:Hd.get(fld,'min'), hi:Hd.get(fld,'max'), cov:Hd.get(fld,'cov')}; }
function ownHtStats(cfg,Hd,fld){
  var key='own|'+cfg+'|'+fld+'|'+state.cut; if(htLimCache.has(key)) return htLimCache.get(key);
  var A=ownHtArrays(Hd,fld), log=isLogHt(fld), signed=(fld==='UN'||fld==='VN'), tr=function(v){ return log?(v>0?Math.log10(v):NaN):v; }, vals=[], xlo=Infinity, xhi=-Infinity, k;
  for(k=0;k<NT*NK;k++){ if(!htShown(A,k)) continue; var m=tr(A.m[k]); if(!(m===m)) continue; vals.push(m); var l=tr(A.lo[k]), h=tr(A.hi[k]); if(l===l && l<xlo) xlo=l; if(h===h && h>xhi) xhi=h; if(m<xlo) xlo=m; if(m>xhi) xhi=m; }
  vals.sort(function(a,b){return a-b;}); var n=vals.length, lo=n?vals[Math.floor(0.005*(n-1))]:0, hi=n?vals[Math.floor(0.995*(n-1))]:1;
  if(signed){ var lim=niceUp(Math.max(Math.abs(lo),Math.abs(hi))||1); lo=-lim; hi=lim; }
  else if(log){ lo=Math.floor(lo*10)/10; hi=Math.ceil(hi*10)/10; if(!(hi>lo)) hi=lo+0.1; }
  else { var st=tickStep(lo,hi,5); lo=Math.floor(lo/st)*st; hi=Math.ceil(hi/st)*st; if(!(hi>lo)) hi=lo+st; }
  var quiet=new Float32Array(NK);
  for(var z=0;z<NK;z++){ var s=0,c=0; for(var f=0;f<NT;f++){ if(FH[f]>=48) continue; var kk=f*NK+z; if(htShown(A,kk)){ var v=tr(A.m[kk]); if(v===v){ s+=v; c++; } } } quiet[z]=c?s/c:NaN; }
  if(!(xlo<xhi)){ xlo=lo; xhi=hi; }
  var R={lo:lo,hi:hi,log:log,signed:signed,xlo:xlo,xhi:xhi,quiet:quiet,tr:tr}; htLimCache.set(key,R); return R; }
function ownValText(v,fld){ var u=ownUnit(fld); if(!(v===v)) return 'No value'; var s=isLogHt(fld)? sciText(v,3) : (Math.abs(v)>=100? v.toFixed(0) : (Math.abs(v)>=1? v.toFixed(2) : v.toPrecision(3))); return s+(u?' '+u:''); }
function renderC(){
  var oc=shownCfg(), wrap=cC1.parentNode, W1=wrap.clientWidth, mL=46, mR=oc?100:64, mB=36, pw=W1-mL-mR, ph=Math.max(180,Math.min(340,pw*0.55)), TF='500 13px '+UI;
  var p=state.pair, fld=state.htField, stat=state.htStat, unit=unitOf(fld);
  var statName=stat==='dom'?'Global-mean difference':(unit==='%'?'Normalized typical difference':'Typical difference');
  var tl=IDX? (oc? splitTitle([ownTitle(oc)+'   '+FIELD_CN[fld], 'Global mean'+(ownUnit(fld)?' ('+ownUnit(fld)+')':'')],' · ',TF,Math.max(120,W1-mL-8))
    : splitTitle([pairLabel(p)+'   '+FIELD_CN[fld], statName+' ('+unit+')'],' · ',TF,Math.max(120,W1-mL-8))) : [''];
  var mT=tl.length>1?50:34;
  var ctx=fit(cC1,W1,ph+mT+mB); rectC=null;
  var W2=cC2.parentNode.clientWidth, H2=ph+mT+mB, c2=fit(cC2,W2,H2);
  if(!IDX) return;
  tl.forEach(function(s,n){ text(ctx,s,mL,14+16*n,{font:TF,color:TOK.ink}); });
  if(oc){ renderCOwn(oc,fld,ctx,c2,mL,mT,pw,ph,W2); return; }
  var Hd=htFor(p);""")
# own branch of view C, inserted before the mousemove handler of cC1
rep("""cC1.addEventListener('mousemove',function(e){ if(!rectC){ tipC.hidden=true; return; } var r=cC1.getBoundingClientRect(), x=e.clientX-r.left-rectC.x, y=e.clientY-r.top-rectC.y;
  if(x<0||y<0||x>=rectC.w||y>=rectC.h){ tipC.hidden=true; return; }
  var Hd=htFor(state.pair); if(!Hd||Hd.error){ tipC.hidden=true; return; }
  var h=Math.min(96,Math.floor(x/rectC.w*97)), zi=NK-1-Math.min(NK-1,Math.floor(y/rectC.h*NK)), f=-1;
  for(var q=0;q<NT;q++){ if(Math.round(FH[q])===h){ f=q; break; } }
  var unit=unitOf(state.htField), s=hourStr(h)+' · '+KMH[zi]+' km · ';
  if(f<0 || Hd.ts[f]<0) s+='Not exported at this time';
  else { var A=htArrays(Hd,state.htField,state.htStat), k=f*NK+zi, v=A.m[k], cv=A.cov?A.cov[k]:NaN;
    if(!(v===v)) s+='No value'; else { s+=(v>0?'+':'')+v.toFixed(2)+(unit==='%'?'%':' '+unit); if(cv===cv) s+=' · coverage '+cv.toFixed(0)+'%'; if(state.cut && !(cv>=50)) s+=' (treated as missing)'; } }""",
"""function renderCOwn(oc,fld,ctx,c2,mL,mT,pw,ph,W2){
  var Hd=ownHtFor(oc), m=stateMsg(Hd,'height–time data'); if(m){ msgBox(ctx,mL,mT,pw,ph,m); return; }
  var A=ownHtArrays(Hd,fld); if(!A.m){ msgBox(ctx,mL,mT,pw,ph,'This quantity was not exported'); return; }
  var S=ownHtStats(oc,Hd,fld), tr=S.tr, R={lo:S.lo,hi:S.hi,log:S.log}, lim=S.signed?S.hi:0;
  if(htOff.width!==97 || htOff.height!==NK){ htOff.width=97; htOff.height=NK; htX=htOff.getContext('2d'); htImg=htX.createImageData(97,NK); }
  var d=htImg.data, sr=TOK.surfRGB, colHas=new Int16Array(97).fill(-1);
  for(var f=0;f<NT;f++){ var H=Math.round(FH[f]); if(H>=0 && H<=96 && Hd.ts[f]>=0) colHas[H]=f; }
  for(var zi=0;zi<NK;zi++){ var r=NK-1-zi; for(var t=0;t<97;t++){ var o=(r*97+t)*4, ff=colHas[t], v=NaN;
    if(ff>=0){ var kk=ff*NK+zi; if(htShown(A,kk)) v=tr(A.m[kk]); }
    if(v===v){ var q=(S.signed?cidx(v,lim):sidx(v,R))*3, T=S.signed?LUT:LUTS; d[o]=T[q]; d[o+1]=T[q+1]; d[o+2]=T[q+2]; } else { d[o]=sr[0]; d[o+1]=sr[1]; d[o+2]=sr[2]; }
    d[o+3]=255; } }
  htX.putImageData(htImg,0,0); ctx.imageSmoothingEnabled=false; ctx.drawImage(htOff,mL,mT,pw,ph);
  if(state.hatch){ ctx.save(); ctx.beginPath(); var any=false, cw=pw/97, ch=ph/NK;
    for(var zj=0;zj<NK;zj++){ var rr=NK-1-zj; for(var tt=0;tt<97;tt++){ var f2=colHas[tt]; if(f2>=0 && !(htShown(A,f2*NK+zj) && tr(A.m[f2*NK+zj])===tr(A.m[f2*NK+zj]))){ ctx.rect(mL+tt*cw,mT+rr*ch,cw+0.3,ch+0.3); any=true; } } }
    if(any){ ctx.fillStyle=hatchFill(ctx); ctx.fill(); } ctx.restore(); }
  ctx.save(); ctx.fillStyle=TOK.veil; var cw2=pw/97, run=-1;
  for(var t2=0;t2<=97;t2++){ var no=t2<97 && colHas[t2]<0; if(no && run<0) run=t2; if(!no && run>=0){ ctx.fillRect(mL+run*cw2,mT,(t2-run)*cw2,ph);
      if((t2-run)*cw2>90) text(ctx,'No data',mL+(run+t2)/2*cw2,mT+ph/2,{align:'center',base:'middle',font:'11px '+UI,color:TOK.ink2}); ctx.fillStyle=TOK.veil; run=-1; } }
  ctx.restore();
  bandsX(ctx,mL,mT-14,pw,12,true,10);
  ctx.strokeStyle=TOK.axis; ctx.lineWidth=1; ctx.strokeRect(mL+0.5,mT+0.5,pw-1,ph-1);
  [0,24,48,72,96].forEach(function(h){ var X=mL+(h+0.5)/97*pw; ctx.beginPath(); ctx.moveTo(X,mT+ph); ctx.lineTo(X,mT+ph+3); ctx.stroke();
    text(ctx,'7/'+(5+h/24),X,mT+ph+6,{align:h===0?'left':(h===96?'right':'center'),base:'top'}); });
  var zt=[100,200,300,400,500,600]; zt.forEach(function(z){ var Y=kmY(z,mT,ph); ctx.beginPath(); ctx.moveTo(mL,Y); ctx.lineTo(mL-3,Y); ctx.stroke(); text(ctx,String(z),mL-5,Y,{align:'right',base:'middle'}); });
  ctx.save(); ctx.translate(11,mT+ph/2); ctx.rotate(-Math.PI/2); text(ctx,'Height (km)',0,0,{align:'center',base:'middle',font:'11.5px '+UI,color:TOK.ink2}); ctx.restore();
  var Xc=mL+(FH[state.f]+0.5)/97*pw; ctx.strokeStyle=TOK.accent; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(Xc,mT); ctx.lineTo(Xc,mT+ph); ctx.stroke(); ctx.lineWidth=1;
  var unit=ownUnit(fld); if(S.signed) drawBar(ctx,mL+pw+14,mT+12,12,ph-16,lim,unit); else drawBarSeq(ctx,mL+pw+14,mT+12,12,ph-16,R,unit);
  rectC={x:mL,y:mT,w:pw,h:ph};
  /* profile at the current time, in the same (log or linear) space */
  var qL=40, qR=12, qw=W2-qL-qR, lo=S.xlo, hi=S.xhi; if(S.signed){ lo=Math.min(0,lo); hi=Math.max(0,hi); } var padv=(hi-lo)*0.06||1; lo-=padv; hi+=padv;
  var X=function(v){ return qL+(v-lo)/(hi-lo)*qw; }, Y=function(z){ return kmY(z,mT,ph); };
  text(c2,frameLabel(state.f),qL,14,{font:'500 13px '+UI,color:TOK.ink});
  c2.strokeStyle=TOK.grid; c2.lineWidth=1;
  var ticks=S.log? logTicks(lo,hi,4) : niceTicks(lo,hi,4).map(function(v){ return {v:v,s:fmtLin(v,hi-lo)}; });
  ticks.forEach(function(t){ var x=X(t.v); c2.beginPath(); c2.moveTo(x,mT); c2.lineTo(x,mT+ph); c2.stroke(); text(c2,t.s,x,mT+ph+6,{align:'center',base:'top',font:(S.log?'10px ':'11px ')+MONO}); });
  zt.forEach(function(z){ text(c2,String(z),qL-5,Y(z),{align:'right',base:'middle'}); });
  c2.strokeStyle=TOK.axis; if(S.signed && lo<0 && hi>0){ c2.beginPath(); c2.moveTo(X(0),mT); c2.lineTo(X(0),mT+ph); c2.stroke(); } c2.strokeRect(qL+0.5,mT+0.5,qw-1,ph-1);
  var fcur=state.f, base=fcur*NK, z2, started;
  c2.save(); c2.strokeStyle=TOK.muted; c2.lineWidth=1.5; c2.setLineDash([5,4]); c2.beginPath(); started=false;
  for(z2=0;z2<NK;z2++){ var qv=S.quiet[z2]; if(!(qv===qv)){ started=false; continue; } if(!started){ c2.moveTo(X(qv),Y(KMH[z2])); started=true; } else c2.lineTo(X(qv),Y(KMH[z2])); }
  c2.stroke(); c2.restore();
  if(Hd.ts[fcur]<0){ text(c2,'Not available at this time',qL+qw/2,mT+ph/2,{align:'center',base:'middle',font:'12px '+UI,color:TOK.ink2}); }
  else {
    var ok=function(z){ var k=base+z; return htShown(A,k) && tr(A.m[k])===tr(A.m[k]) && tr(A.lo[k])===tr(A.lo[k]) && tr(A.hi[k])===tr(A.hi[k]); };
    c2.save(); c2.fillStyle=TOK.ink; c2.globalAlpha=0.14; var segs=[], cur=[];
    for(z2=0;z2<NK;z2++){ if(ok(z2)) cur.push(z2); else if(cur.length){ segs.push(cur); cur=[]; } } if(cur.length) segs.push(cur);
    segs.forEach(function(sg){ c2.beginPath(); sg.forEach(function(zz,n){ var px=X(tr(A.lo[base+zz])), py=Y(KMH[zz]); if(n) c2.lineTo(px,py); else c2.moveTo(px,py); });
      for(var n2=sg.length-1;n2>=0;n2--){ var zz2=sg[n2]; c2.lineTo(X(tr(A.hi[base+zz2])),Y(KMH[zz2])); } c2.closePath(); c2.fill(); });
    c2.restore();
    c2.strokeStyle=TOK.ink; c2.lineWidth=2; c2.beginPath(); started=false;
    for(z2=0;z2<NK;z2++){ var mv=tr(A.m[base+z2]); if(!htShown(A,base+z2) || !(mv===mv)){ started=false; continue; } if(!started){ c2.moveTo(X(mv),Y(KMH[z2])); started=true; } else c2.lineTo(X(mv),Y(KMH[z2])); }
    c2.stroke(); c2.lineWidth=1;
  }
  text(c2,unit,qL+qw,mT+ph+20,{align:'right',base:'top',font:'11px '+MONO});
  $('legC').firstElementChild.nextElementSibling.style.display='';
}
cC1.addEventListener('mousemove',function(e){ if(!rectC){ tipC.hidden=true; return; } var r=cC1.getBoundingClientRect(), x=e.clientX-r.left-rectC.x, y=e.clientY-r.top-rectC.y;
  if(x<0||y<0||x>=rectC.w||y>=rectC.h){ tipC.hidden=true; return; }
  var oc=shownCfg(), Hd=oc?ownHtFor(oc):htFor(state.pair); if(!Hd||Hd.error){ tipC.hidden=true; return; }
  var h=Math.min(96,Math.floor(x/rectC.w*97)), zi=NK-1-Math.min(NK-1,Math.floor(y/rectC.h*NK)), f=-1;
  for(var q=0;q<NT;q++){ if(Math.round(FH[q])===h){ f=q; break; } }
  var unit=unitOf(state.htField), s=hourStr(h)+' · '+KMH[zi]+' km · ';
  if(f<0 || Hd.ts[f]<0) s+=oc?'Not available at this time':'Not exported at this time';
  else if(oc){ var Ao=ownHtArrays(Hd,state.htField), ko=f*NK+zi, vo=Ao.m?Ao.m[ko]:NaN, co=Ao.cov?Ao.cov[ko]:NaN;
    s+=ownValText(vo,state.htField); if(co===co) s+=' · coverage '+co.toFixed(0)+'%'; if(state.cut && !(co>=50)) s+=' (treated as missing)'; }
  else { var A=htArrays(Hd,state.htField,state.htStat), k=f*NK+zi, v=A.m[k], cv=A.cov?A.cov[k]:NaN;
    if(!(v===v)) s+='No value'; else { s+=(v>0?'+':'')+v.toFixed(2)+(unit==='%'?'%':' '+unit); if(cv===cv) s+=' · coverage '+cv.toFixed(0)+'%'; if(state.cut && !(cv>=50)) s+=' (treated as missing)'; } }""")
# ---- UI: Show segment
rep("""  sel.value=state.pair; sel.addEventListener('change',function(){ state.pair=sel.value; renderAll('pair'); });""",
"""  sel.value=state.pair; sel.addEventListener('change',function(){ state.pair=sel.value; syncShow(); renderAll('pair'); });
  Array.prototype.forEach.call(showSeg.children,function(b){ b.addEventListener('click',function(){ if(b.disabled) return; state.show=b.getAttribute('data-show'); syncShow(); renderAll('show'); }); });
  syncShow();""")
rep("""function describeData(){""",
"""var showSeg=$('showSeg');
function syncShow(){ var xy=pairXY(state.pair), bs=showSeg.children, own=!!(IDX&&IDX.own);
  bs[0].textContent=cfgShort(xy[0])+' − '+cfgShort(xy[1]); bs[1].textContent=cfgShort(xy[0]); bs[2].textContent=cfgShort(xy[1]);
  bs[1].disabled=!own||!IDX.own.configs[xy[0]]; bs[2].disabled=!own||!IDX.own.configs[xy[1]];
  if((state.show==='X'&&bs[1].disabled)||(state.show==='Y'&&bs[2].disabled)) state.show='diff';
  Array.prototype.forEach.call(bs,function(b){ b.setAttribute('aria-pressed',b.getAttribute('data-show')===state.show?'true':'false'); });
  var o=state.show!=='diff'; $('optDots').disabled=o; Array.prototype.forEach.call($('htStatSeg').children,function(b){ b.disabled=o; }); }
function describeData(){""")
# ---- footnote
rep("""  para('GRACE-FO: each orbit runs from one ascending node to the next;""",
"""  para('The field itself (one configuration shown instead of the difference): the 10-member mean at the fixed heights, encoded in 254 steps between the 0.1 and 99.9 percentiles of all times of that configuration (values outside are marked ≤ or ≥ in the tooltip); DEN in kg m⁻³, NE and NmF2 in cm⁻³. The colour range is the encoding range of X and Y together, so that switching between them compares like with like. Height–time: area-weighted global mean, member minimum and maximum of the member-mean field, with the same coverage rule as for the differences.');
  para('GRACE-FO: each orbit runs from one ascending node to the next;""")
# ---- exported API for the 3D script
rep("""window.TIEGCMPage={ state:state, mapsFor:mapsFor, mapLim:mapLim, unitOf:unitOf, pairLabel:pairLabel,""",
"""window.TIEGCMPage={ state:state, mapsFor:mapsFor, mapLim:mapLim, unitOf:unitOf, pairLabel:pairLabel, ownFor:ownFor, ownRange:ownRange, shownCfg:shownCfg, logTicks:logTicks,""")
# ---- 3D script
rep("""function scale(){ var T=D.tokens(); return T.div.map(function(c,i){ return [i/10, rgb(c)]; }); }
function layers(){ var s=D.state, A=D.axes(), M=D.mapsFor(s.pair,s.field); if(!M || M.error || M.codes.length<A.KMS.length) return null;
  var out=[], base=s.f*A.N, lim=0;
  A.KMS.forEach(function(km,h){ lim=Math.max(lim,D.mapLim(s.pair,s.field,km)); var codes=M.codes[h], sc=M.s[h], zz=[], cc=[];
    for(var i=0;i<A.NLAT;i++){ var zr=[], cr=[]; for(var j=0;j<A.NLT;j++){ var c=codes[base+i*A.NLT+j]; if(c===255){ zr.push(null); cr.push(null); } else { zr.push(km); cr.push((c-127)*sc); } } zz.push(zr); cc.push(cr); }
    out.push({z:zz,c:cc}); });
  return {L:out,lim:lim}; }""",
"""function scale(){ var T=D.tokens(); return T.div.map(function(c,i){ return [i/10, rgb(c)]; }); }
function scaleSeq(){ var T=D.tokens(); return T.seq.map(function(c,i){ return [i/(T.seq.length-1), rgb(c)]; }); }
function layers(){ var s=D.state, A=D.axes(), oc=D.shownCfg(), M=oc?D.ownFor(oc,s.field):D.mapsFor(s.pair,s.field); if(!M || M.error || M.codes.length<A.KMS.length) return null;
  var out=[], base=s.f*A.N, lim=0, lo=Infinity, hi=-Infinity, R=null;
  if(oc){ A.KMS.forEach(function(km){ var r=D.ownRange(s.field,km); if(r){ lo=Math.min(lo,r.lo); hi=Math.max(hi,r.hi); R=r; } }); if(!R) return null; }
  A.KMS.forEach(function(km,h){ if(!oc) lim=Math.max(lim,D.mapLim(s.pair,s.field,km)); var codes=M.codes[h], sc=M.s[h], ol=oc?M.lo[h]:0, zz=[], cc=[];
    for(var i=0;i<A.NLAT;i++){ var zr=[], cr=[]; for(var j=0;j<A.NLT;j++){ var c=codes[base+i*A.NLT+j]; if(c===255){ zr.push(null); cr.push(null); } else { zr.push(km); cr.push(oc?(ol+c*sc):(c-127)*sc); } } zz.push(zr); cc.push(cr); }
    out.push({z:zz,c:cc}); });
  var o={L:out,lim:lim,own:!!oc};
  if(oc){ o.cmin=lo; o.cmax=hi; o.unit=M.unit||''; o.cs=scaleSeq(); if(R.log){ var tk=D.logTicks(lo,hi,6); o.tickvals=tk.map(function(t){return t.v;}); o.ticktext=tk.map(function(t){return t.s;}); } else { o.tickvals=null; o.ticktext=null; } }
  else { o.cmin=-lim; o.cmax=lim; o.unit=D.unitOf(s.field); o.cs=scale(); o.tickvals=null; o.ticktext=null; }
  return o; }""")
rep("""  var cs=scale(), x=A.LT.slice(), y=A.LAT.slice(), unit=D.unitOf(s.field);
  var traces=A.KMS.map(function(km,n){ return {type:'surface', x:x, y:y, z:R.L[n].z, surfacecolor:R.L[n].c, cmin:-R.lim, cmax:R.lim, colorscale:cs,
    showscale:n===A.KMS.length-1, colorbar:{title:{text:unit}, thickness:12, len:0.55, tickfont:{color:T.muted,size:10}, outlinewidth:0},""",
"""  var cs=R.cs, x=A.LT.slice(), y=A.LAT.slice(), unit=R.unit;
  var traces=A.KMS.map(function(km,n){ return {type:'surface', x:x, y:y, z:R.L[n].z, surfacecolor:R.L[n].c, cmin:R.cmin, cmax:R.cmax, colorscale:cs,
    showscale:n===A.KMS.length-1, colorbar:{title:{text:unit}, thickness:12, len:0.55, tickfont:{color:T.muted,size:10}, outlinewidth:0, tickvals:R.tickvals, ticktext:R.ticktext},""")
rep("""  built=true; lastKey=s.pair+'|'+s.field+'|'+s.f; return true;""","""  built=true; lastKey=s.pair+'|'+s.field+'|'+s.f+'|'+s.show; return true;""")
rep("""  var s=D.state, key=s.pair+'|'+s.field+'|'+s.f; if(key===lastKey) return;
  if(pending) return; pending=true;
  requestAnimationFrame(function(){ pending=false; var s2=D.state, R=layers(); if(!R) return; var unit=D.unitOf(s2.field), n=R.L.length, idx=[], mins=[], maxs=[];
    for(var i=0;i<n;i++){ idx.push(i); mins.push(-R.lim); maxs.push(R.lim); }
    Plotly.restyle(el,{z:R.L.map(function(o){return o.z;}), surfacecolor:R.L.map(function(o){return o.c;}), cmin:mins, cmax:maxs},idx);
    Plotly.restyle(el,{'colorbar.title.text':unit},[n-1]);
    lastKey=s2.pair+'|'+s2.field+'|'+s2.f; });""",
"""  var s=D.state, key=s.pair+'|'+s.field+'|'+s.f+'|'+s.show; if(key===lastKey) return;
  if(pending) return; pending=true;
  requestAnimationFrame(function(){ pending=false; var s2=D.state, R=layers(); if(!R) return; var n=R.L.length, idx=[], mins=[], maxs=[], css=[];
    for(var i=0;i<n;i++){ idx.push(i); mins.push(R.cmin); maxs.push(R.cmax); css.push(R.cs); }
    Plotly.restyle(el,{z:R.L.map(function(o){return o.z;}), surfacecolor:R.L.map(function(o){return o.c;}), cmin:mins, cmax:maxs, colorscale:css},idx);
    Plotly.restyle(el,{'colorbar.title.text':R.unit, 'colorbar.tickvals':[R.tickvals], 'colorbar.ticktext':[R.ticktext]},[n-1]);
    lastKey=s2.pair+'|'+s2.field+'|'+s2.f+'|'+s2.show; });""")
open(dst,'w',encoding='utf-8').write(s); print('patched4')
