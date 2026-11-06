import json,re,sys
src,dst=sys.argv[1:3]; s=open(src,encoding='utf-8').read()
m=json.load(open('en2zh.json',encoding='utf-8'))
manual={
 "'3.0.1 + NCAR settings'":"'3.0.1 + NCAR 推荐设置'",
 "'full NCAR settings − 3.0.1'":"'整套 NCAR 设置 − 3.0.1'", "'DUFF on − off'":"'开 DUFF − 不开'", "'full NCAR settings − DUFF only'":"'整套 NCAR 设置 − 只开 DUFF'",
 "name:'NCAR settings'":"name:'NCAR 设置'", "name:'Assimilation − control'":"name:'同化 − 对照'", "['Assimilation − control',":"['同化 − 对照',", "'Each pair is an assimilation run minus its own control: the 1-hour forecast of each cycle, member i minus member i, then the 10-member mean. 7/5 00, 7/8 23 and 7/9 00 UT are not available for these pairs.'":"'每组是同化运行减它自己的对照：每个循环的一小时预报，第 i 个成员减第 i 个成员，再取 10 个成员的平均。这几组没有 7/5 00、7/8 23、7/9 00 UT 三帧。'", "['NCAR settings',":"['NCAR 设置',",
 "'N is 3.0.1 with the full NCAR recommended settings; N1 is 3.0.1 with only DUFF turned on. Temperature and hmF2 add exactly; percentages only approximately.'":"'N 是 3.0.1 加整套 NCAR 推荐设置；N1 是 3.0.1 只开 DUFF。温度和 hmF2 严格可加，百分比只近似可加。'",
 "hmF2:'hmF2 F-layer peak height',NmF2:'NmF2 F-layer peak electron density'":"hmF2:'hmF2 F 层峰高',NmF2:'NmF2 F 层峰值电子密度'",
 "'At least one member has no value here'":"'至少一个成员在这里没有值'", "'No global-mean series for '":"'没有全球平均序列：'",
 ">hmF2 and NmF2 are the height and the electron density of the largest Ne in each model column, searched only over the levels at or above 200 km (so a strong E or F1 layer cannot be picked up as the peak), on the model’s own levels without interpolation, computed member by member. The hmF2 difference is in km; the NmF2 difference is in % of the reference. They have no height, so the height buttons do not apply.<":">hmF2 和 NmF2 是每个模式格点垂直柱子里 Ne 最大值的高度和大小，只在 200 km 及以上的层里找（这样强的 E 层或 F1 层不会被当成峰），在模式自己的层上取，不插值，逐个成员算。hmF2 的差单位是 km，NmF2 的差是参考配置的百分比。它们没有高度维，高度按钮对它们不起作用。<",
 ">hmF2 and NmF2 have one value per column, so there is nothing to stack by height here. Choose temperature, density or electron density for this view.<":">hmF2 和 NmF2 每根柱子只有一个值，这里没有可以按高度叠的东西。看这个视图请选温度、密度或电子密度。<",

  ">Height–time<":">高度–时间<", ">Groups<":">分组对比<", ">3D layers<":">3D 叠层<", ">GRACE-FO orbit means<":">GRACE-FO 轨道平均<", ">Experiments<":">实验<", ">COSMIC-2<":">COSMIC-2<",
 'aria-label="Sections"':'aria-label="章节"', 'aria-label="Enlarged figure"':'aria-label="放大的图"', 'aria-label="Experiment"':'aria-label="实验"',
 ">Experiments: fixed figures against observations<":">实验：对观测的固定图<",
 ">Every experiment produces the same set of figures when it finishes: ten for an assimilation run, six for a control run. They compare the 1-hour forecast (and, for assimilation runs, the analysis) with the COSMIC-2 electron density and with the GRACE-FO density. The figures are made on the computing system from the run's own output and copied here unchanged. Click a figure to enlarge it.<":">每个实验跑完都自动出同一套图：同化运行 10 张，对照运行 6 张。它们把一小时预报（同化运行还有分析场）和 COSMIC-2 电子密度、GRACE-FO 密度比较。图在计算机上由该运行自己的输出画出，原样放在这里。点图可以放大。<",
 ">One-hue scale: the field itself, when one configuration is shown instead of the difference<":">单色渐变：只显示一个配置时画的是场本身，不是差<",
 '<span class="lbl">Show</span>':'<span class="lbl">显示</span>',
 'aria-label="Show the difference or one configuration"':'aria-label="显示差还是某一个配置"',
 "'Not available at this time'":"'这个时刻没有'", "'No colour range for this field'":"'这个量没有色标范围'",
 "'Global mean'+(ownUnit(fld)":"'全球平均'+(ownUnit(fld)",
 "'The field itself (one configuration shown instead of the difference): the 10-member mean at the fixed heights, encoded in 254 steps between the 0.1 and 99.9 percentiles of all times of that configuration (values outside are marked ≤ or ≥ in the tooltip); DEN in kg m⁻³, NE and NmF2 in cm⁻³. The colour range is the encoding range of X and Y together, so that switching between them compares like with like. Height–time: area-weighted global mean, member minimum and maximum of the member-mean field, with the same coverage rule as for the differences.'":"'场本身（只显示一个配置时）：固定高度上的 10 成员平均，在该配置全部时刻的 0.1 和 99.9 百分位之间编成 254 级（范围之外的值在悬停提示里标 ≤ 或 ≥）；DEN 单位 kg m⁻³，NE 和 NmF2 单位 cm⁻³。色标范围取 X 和 Y 两者编码范围的并集，这样来回切换时比的是同一个尺子。高度–时间：成员平均场的面积加权全球平均、成员最小和最大，覆盖率规则和差一样。'",
 ">Experiment<":">实验<",
 ">Model-only configurations against COSMIC-2<":">只跑模式的配置对 COSMIC-2<",
 ">Seven configurations of the version comparison, run without assimilation, compared with the COSMIC-2 electron density profiles of the same four days: electron density by height band, and the F-layer peak height hmF2 (height of the largest Ne on each profile between 160 and 500 km, found the same way for observation and model). All configurations use the same 490,076 observations: levels not flagged bad in the ionPrf files and with a model value in every run; no DART outlier rejection. Drawn from the tables of the 11/3 computation.<":">版本对照里的七个配置，不做同化，和同样四天的 COSMIC-2 电子密度剖面比较：分高度带的电子密度，以及 F 层峰高 hmF2（每条剖面在 160–500 km 之间 Ne 最大处的高度，观测和模式用同样的取法）。所有配置用同一批 490,076 条观测：ionPrf 文件里没有标坏、而且每个运行都有模式值的层；不做 DART 的离群剔除。由 11/3 那次计算的表画出。<",
 '<a class="lang" id="langLink" href="zh/" lang="zh">中文版</a>':'<a class="lang" id="langLink" href="../" lang="en">English</a>',
 "DATA_BASE='data/full/';":"DATA_BASE='../data/full/';",
 "'All '+nAll+' comparisons have maps'":"nAll+' 组比较都有地图'",
 "<html lang=\"en\">":"<html lang=\"zh\">", "' One color scale for the whole group'":"' 同一组用同一个色标'", ">量<":">物理量<",
}
# paragraphs extended on 2026-11-07 (the aligned table holds the original paragraphs; the extended ones are built from them here)
def _ext(prefix,en_old,en_new,zh_add):
    old=[k for k in m if k.startswith(prefix)]; assert len(old)==1,prefix; old=old[0]
    manual[old.replace(en_old,en_new)]=m[old][:-1]+zh_add+'<'
_ext('>Hourly differences between two configurations:', 'quantity and height.<', 'quantity and height. The buttons after the height choose what is drawn: the difference, or the field of one of the two configurations itself.<', '高度后面的几个按钮选画什么：画差，还是画两个配置中某一个的场本身。')
_ext('>Horizontal axis: local time; vertical axis: latitude;', 'the 10-member mean difference. Hover over', 'the 10-member mean difference, or the 10-member mean of the field itself when one configuration is shown. Hover over', '只显示一个配置时，颜色是该配置场本身的 10 成员平均。')
_ext('>Left: global-mean difference against height and time;', 'the quantity is chosen here.<', 'the quantity is chosen here. When one configuration is shown, the plots give its global mean itself (logarithmic colours and axis for densities and mixing ratios).<', '只显示一个配置时，这里画的是它自己的全球平均（密度和混合比用对数颜色和对数坐标）。')
_ext('>Related comparisons side by side at the same time and height.', 'vertical line: current time.<', 'vertical line: current time. This section always shows differences, whichever Show button is pressed.<', '这一节永远画差，不受“显示”按钮影响。')
n_auto=0
for k in sorted(m,key=len,reverse=True):
    if k in s: s=s.replace(k,m[k]); n_auto+=1
miss=[]
for k,v in manual.items():
    if k in s: s=s.replace(k,v)
    else: miss.append(k[:50])

import re as _re
def _tables(s):
    zh_cfg="var CFG={A:'2.0（Nick 的可执行文件）',Ap:'2.0 重编译',B:'2.9',C:'3.0.1，电子加热选项 4',D:'3.0.1',E:'3.0',F:'3.0.1 开 ENFORCE_N2',G1:'3.0.1，cp 按质量混合比',G2:'3.0.1，O 63 µm 冷却系数 ×2',G3:'3.0.1，去掉 qrj 的 5%',H:'2.0，平均分子量加氦',I1:'2.0 + Joule 加热 w 修复',I2:'2.0 + elam3d 修复',I3:'2.0 + filter 修复',N:'3.0.1 + NCAR 推荐设置',N1:'3.0.1 + DUFF',exp6:'2.0，同化（exp6）',ctrl95:'2.0，对照（ctrl95）',v3exp1:'3.0.1 默认，同化',v3ctrl:'3.0.1 默认，对照',v3exp1_duff:'3.0.1 + DUFF，同化',v3ctrl_duff:'3.0.1 + DUFF，对照'};"
    zh_sub="var PAIR_SUB={'B-Ap':'2.9 − 2.0','C-B':'3.0.1（加热 4）− 2.9','D-C':'加热选项 6 − 4','D-Ap':'3.0.1 − 2.0','D-E':'3.0.1 − 3.0','D-F':'3.0.1 关 − 开 ENFORCE_N2','F-E':'3.0.1 开 ENFORCE_N2 − 3.0','I1-Ap':'2.0 加 Joule 加热 w 修复','I2-Ap':'2.0 加 elam3d 修复','I3-Ap':'2.0 加 filter 修复','G1-D':'cp 按质量混合比','G2-D':'O 63 µm 系数 ×2','G3-D':'去掉 qrj 的 5%','H-Ap':'2.0 平均分子量加氦','N-D':'整套 NCAR 设置 − 3.0.1','N1-D':'开 DUFF − 不开','N-N1':'整套 NCAR 设置 − 只开 DUFF','N1-Ap':'3.0.1 + DUFF − 2.0','exp6-ctrl95':'2.0：同化 − 对照','v3exp1-v3ctrl':'3.0.1：同化 − 对照','v3exp1_duff-v3ctrl_duff':'3.0.1 + DUFF：同化 − 对照'};"
    zh_fld="var FIELD_CN={TN:'TN 中性温度',DEN:'DEN 中性质量密度',NE:'NE 电子密度',UN:'UN 纬向风（向东为正）',VN:'VN 经向风（向北为正）',O2:'O2',O1:'O1',N2:'N2',OP:'OP（O⁺）',HE:'HE',NO:'NO',NO_COOL:'NO_COOL',O_N2:'O_N2',hmF2:'hmF2 F 层峰高',NmF2:'NmF2 F 层峰值电子密度'};"
    zh_map="var MAPF_CN={TN:'温度',DEN:'密度',NE:'电子密度',hmF2:'hmF2',NmF2:'NmF2'};"
    for name,new in (('CFG',zh_cfg),('PAIR_SUB',zh_sub),('FIELD_CN',zh_fld),('MAPF_CN',zh_map)):
        s,n=_re.subn(r'var %s=\{.*?\};'%name,lambda m:new,s,count=1,flags=_re.S); assert n==1,name
    return s
s=_tables(s)

open(dst,'w',encoding='utf-8').write(s)
print('auto replaced',n_auto,'of',len(m),'; manual missing:',miss)
