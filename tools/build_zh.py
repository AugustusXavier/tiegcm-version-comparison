import json,re,sys
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
m=json.load(open('en2zh.json',encoding='utf-8'))
manual={
 "'3.0.1 + NCAR settings'":"'3.0.1 + NCAR 推荐设置'",
 "'full NCAR settings − 3.0.1'":"'整套 NCAR 设置 − 3.0.1'", "'DUFF on − off'":"'开 DUFF − 不开'", "'full NCAR settings − DUFF only'":"'整套 NCAR 设置 − 只开 DUFF'",
 "name:'NCAR settings'":"name:'NCAR 设置'", "['NCAR settings',":"['NCAR 设置',",
 "'N is 3.0.1 with the full NCAR recommended settings; N1 is 3.0.1 with only DUFF turned on. Temperature and hmF2 add exactly; percentages only approximately.'":"'N 是 3.0.1 加整套 NCAR 推荐设置；N1 是 3.0.1 只开 DUFF。温度和 hmF2 严格可加，百分比只近似可加。'",
 "hmF2:'hmF2 F-layer peak height',NmF2:'NmF2 F-layer peak electron density'":"hmF2:'hmF2 F 层峰高',NmF2:'NmF2 F 层峰值电子密度'",
 "'At least one member has no value here'":"'至少一个成员在这里没有值'", "'No global-mean series for '":"'没有全球平均序列：'",
 ">hmF2 and NmF2 are the height and the electron density of the largest Ne in each model column, over the whole column, on the model’s own levels without interpolation, computed member by member. Where the F layer is weak the largest Ne can sit in the lower ionosphere, so hmF2 can jump by a few hundred km. The hmF2 difference is in km; the NmF2 difference is in % of the reference. They have no height, so the height buttons do not apply.<":">hmF2 和 NmF2 是每个模式格点垂直柱子里 Ne 最大值的高度和大小，在整根柱子、模式自己的层上取，不插值，逐个成员算。F 层弱的地方最大值可能落到低层电离层，hmF2 会跳几百公里。hmF2 的差单位是 km，NmF2 的差是参考配置的百分比。它们没有高度维，高度按钮对它们不起作用。<",
 ">hmF2 and NmF2 have one value per column, so there is nothing to stack by height here. Choose temperature, density or electron density for this view.<":">hmF2 和 NmF2 每根柱子只有一个值，这里没有可以按高度叠的东西。看这个视图请选温度、密度或电子密度。<",
 ">Scope.<":">范围。<",
 "</b> The maps and curves in the first five sections show differences between configurations only; they do not show which configuration is closer to the observations. Comparisons with observations are in the GRACE-FO section and in the two sections at the end.<":"</b>前五节的地图和曲线只显示配置之间的差，不表示哪个配置更接近观测。和观测的比较在 GRACE-FO 一节和最后两节。<",
  ">Height–time<":">高度–时间<", ">Groups<":">分组对比<", ">3D layers<":">3D 叠层<", ">GRACE-FO orbit means<":">GRACE-FO 轨道平均<", ">Experiments<":">实验<", ">COSMIC-2<":">COSMIC-2<",
 'aria-label="Sections"':'aria-label="章节"', 'aria-label="Enlarged figure"':'aria-label="放大的图"', 'aria-label="Experiment"':'aria-label="实验"',
 ">Experiments: fixed figures against observations<":">实验：对观测的固定图<",
 ">Every assimilation experiment produces the same seven figures when it finishes; control runs produce three. They compare the 1-hour forecast (and, for assimilation runs, the analysis) with the COSMIC-2 electron density and with the GRACE-FO density. The figures are made on the computing system from the run's own output and copied here unchanged. Click a figure to enlarge it.<":">每个同化实验跑完都自动出同样的 7 张图，对照运行出 3 张。它们把一小时预报（同化运行还有分析场）和 COSMIC-2 电子密度、GRACE-FO 密度比较。图在计算机上由该运行自己的输出画出，原样放在这里。点图可以放大。<",
 ">Experiment<":">实验<",
 ">Model-only configurations against COSMIC-2<":">只跑模式的配置对 COSMIC-2<",
 ">Seven configurations of the version comparison, run without assimilation, compared with the COSMIC-2 electron density profiles of the same four days: electron density by height band, and the F-layer peak height hmF2 (height of the largest Ne on each profile between 160 and 500 km, found the same way for observation and model). All configurations use the same 490,076 observations: levels not flagged bad in the ionPrf files and with a model value in every run; no DART outlier rejection. Drawn from the tables of the 11/3 computation.<":">版本对照里的七个配置，不做同化，和同样四天的 COSMIC-2 电子密度剖面比较：分高度带的电子密度，以及 F 层峰高 hmF2（每条剖面在 160–500 km 之间 Ne 最大处的高度，观测和模式用同样的取法）。所有配置用同一批 490,076 条观测：ionPrf 文件里没有标坏、而且每个运行都有模式值的层；不做 DART 的离群剔除。由 11/3 那次计算的表画出。<",
 '<a class="lang" id="langLink" href="zh/" lang="zh">中文版</a>':'<a class="lang" id="langLink" href="../" lang="en">English</a>',
 "DATA_BASE='data/full/';":"DATA_BASE='../data/full/';",
 "'All '+nAll+' comparisons have maps'":"nAll+' 组比较都有地图'",
 "<html lang=\"en\">":"<html lang=\"zh\">", "' One color scale for the whole group'":"' 同一组用同一个色标'", ">量<":">物理量<",
}
n_auto=0
for k in sorted(m,key=len,reverse=True):
    if k in s: s=s.replace(k,m[k]); n_auto+=1
miss=[]
for k,v in manual.items():
    if k in s: s=s.replace(k,v)
    else: miss.append(k[:50])

import re as _re
def _tables(s):
    zh_cfg="var CFG={A:'2.0（Nick 的可执行文件）',Ap:'2.0 重编译',B:'2.9',C:'3.0.1，电子加热选项 4',D:'3.0.1',E:'3.0',F:'3.0.1 开 ENFORCE_N2',G1:'3.0.1，cp 按质量混合比',G2:'3.0.1，O 63 µm 冷却系数 ×2',G3:'3.0.1，去掉 qrj 的 5%',H:'2.0，平均分子量加氦',I1:'2.0 + Joule 加热 w 修复',I2:'2.0 + elam3d 修复',I3:'2.0 + filter 修复',N:'3.0.1 + NCAR 推荐设置',N1:'3.0.1 + DUFF'};"
    zh_sub="var PAIR_SUB={'B-Ap':'2.9 − 2.0','C-B':'3.0.1（加热 4）− 2.9','D-C':'加热选项 6 − 4','D-Ap':'3.0.1 − 2.0','D-E':'3.0.1 − 3.0','D-F':'3.0.1 关 − 开 ENFORCE_N2','F-E':'3.0.1 开 ENFORCE_N2 − 3.0','I1-Ap':'2.0 加 Joule 加热 w 修复','I2-Ap':'2.0 加 elam3d 修复','I3-Ap':'2.0 加 filter 修复','G1-D':'cp 按质量混合比','G2-D':'O 63 µm 系数 ×2','G3-D':'去掉 qrj 的 5%','H-Ap':'2.0 平均分子量加氦','N-D':'整套 NCAR 设置 − 3.0.1','N1-D':'开 DUFF − 不开','N-N1':'整套 NCAR 设置 − 只开 DUFF','N1-Ap':'3.0.1 + DUFF − 2.0'};"
    zh_fld="var FIELD_CN={TN:'TN 中性温度',DEN:'DEN 中性质量密度',NE:'NE 电子密度',UN:'UN 纬向风（向东为正）',VN:'VN 经向风（向北为正）',O2:'O2',O1:'O1',N2:'N2',OP:'OP（O⁺）',HE:'HE',NO:'NO',NO_COOL:'NO_COOL',O_N2:'O_N2',hmF2:'hmF2 F 层峰高',NmF2:'NmF2 F 层峰值电子密度'};"
    zh_map="var MAPF_CN={TN:'温度',DEN:'密度',NE:'电子密度',hmF2:'hmF2',NmF2:'NmF2'};"
    for name,new in (('CFG',zh_cfg),('PAIR_SUB',zh_sub),('FIELD_CN',zh_fld),('MAPF_CN',zh_map)):
        s,n=_re.subn(r'var %s=\{.*?\};'%name,lambda m:new,s,count=1,flags=_re.S); assert n==1,name
    return s
s=_tables(s)

open(dst,'w',encoding='utf-8').write(s)
print('auto replaced',n_auto,'of',len(m),'; manual missing:',miss)
