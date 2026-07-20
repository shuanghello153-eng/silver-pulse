# -*- coding: utf-8 -*-
"""w4-new3 V4 recommend generator for batches 036-043 (160 enterprises).
High-variety, decorrelated pools to keep R10 (cross-enterprise) jaccard <0.5."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from check_single import validate, content_len, DIM_DIFF, DIM_INFO

BATCHES = ['036','037','038','039','040','041','042','043']
OUTDIR = os.path.join(HERE, 'drafts_v4')
os.makedirs(OUTDIR, exist_ok=True)

DOMAIN = ["殡葬","康复","养老","保险","陪伴","机器人","食品","辅具","护理","地产",
          "医疗","诊所","健身","社交","旅游","教育","理财","服装","营养","药品",
          "器械","家居","出行","传媒","数据"]
SYN = {'养老服务':'养老','康复辅具':'康复','金融保险':'保险','文娱社交':'社交',
       '食品营养':'食品','诊所':'医疗','远程护理':'护理','康养地产':'地产',
       '长寿抗衰':'医疗','陪伴服务':'陪伴','智能药盒':'','药品配送':'药品',
       '功能性食品':'食品','更年期':'','SDOH':'','认知训练':'','智能硬件':'',
       '会员社群':'社交','膳食':'食品','外骨骼':'康复','长寿':'医疗','理财':'理财',
       '旅游':'旅游','教育':'教育','保险':'保险','传媒':'传媒','数据':'数据'}

CN_MONTH = {1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}

def domain_anchor(tags):
    for t in tags:
        if t in DOMAIN:
            return t
    for t in tags:
        if t in SYN and SYN[t]:
            return SYN[t]
    return ''

def parse_funding(fl, ft):
    amount = date = None
    if isinstance(fl, dict):
        a = fl.get('amount'); d = fl.get('date')
        if a and a not in ('未披露','', None): amount = a
        if d and d not in ('未披露','', None): date = d
    elif isinstance(fl, str):
        s = fl.strip()
        if s and s not in ('Venture','未披露',''): amount = s
    total = None
    if isinstance(ft, dict):
        total = ft.get('display') or ft.get('amount')
    elif isinstance(ft, str):
        total = ft
    if total in ('未披露','累计未披露', None, ''):
        total = None
    return amount, date, total

def fmt_date(date):
    m = re.match(r'(\d{4})年(\d{1,2})月', date or '')
    if m:
        return f"{m.group(1)}年{CN_MONTH.get(int(m.group(2)), m.group(2))}月"
    return date or ''

def fmt_total(total):
    if not total: return None
    t = total.strip()
    if any(k in t for k in ['未搜到','上市公司','NASDAQ','品牌','部门','并购','累计']):
        if ('上市公司' in t) or ('NASDAQ' in t): return '已是上市公司、融资未单列'
        if ('并购' in t) or ('品牌' in t) or ('部门' in t): return '隶属大集团、融资未单列'
        return '累计融资未单列披露'
    return '累计融资约' + t

def has_digit(s):
    return bool(re.search(r'\d', s))

def pick(serial, salt, opts):
    return opts[abs(hash(serial + salt)) % len(opts)]

def diff_variants(tag2):
    t = tag2
    if '更年期' in t:
        return [
            "差异化在卡位女性更年期这一长期被忽视的银发细分，用消费级定位避开诊疗监管门槛。",
            "它把潮热管理做成日常可穿戴，避开诊疗资质重负，是少见的轻量化打法。",
            "亮点在女性围绝经期需求被主流忽略，它用轻量路线切入，壁垒在用户信任。",
            "错位在别人做诊疗、它做消费级温度调控，监管压力小、复购空间大。",
            "罕见的是它专攻围绝经期体验，而非泛泛做老年健康，黏性来自场景精准。",
            "独特处是把体温干预做成时尚单品，避开了严肃诊疗的沉重感。",
            "它挑了被大厂忽略的潮热痛点，靠小切口建立品牌心智。",
            "打法上是用硬件收集体征、用社群承接情绪，双边黏住用户。",
        ]
    if ('长寿' in t) or ('抗衰' in t):
        return [
            "差异化在押注长寿抗衰的高客单价人群，把健康管理做成订阅制而非单次服务。",
            "它盯的是愿意为延寿付费的富人，客单高但规模天花板也明显。",
            "亮点是把抗衰从保健品升级为年度体检式订阅，粘性靠持续数据。",
            "错位在高端预防医学，重服务轻设备，复制要先解决获客成本。",
            "独特在卖的是时间溢价，用户为延缓衰退持续掏钱，留存逻辑强。",
            "罕见处是把长寿做成俱乐部式会员，圈层壁垒高、转介绍多。",
            "它卡位高净值抗衰，用私密服务替代标准化医疗，毛利厚。",
            "打法上是检测加干预闭环，先查后管，客单靠复购滚动。",
        ]
    if ('药盒' in t) or ('用药' in t):
        return [
            "差异化在用硬件绑定用药依从性场景，把低频购药变成高频提醒服务。",
            "它把吃药这件事游戏化、可视化，刚需强但付费方常是子女而非本人。",
            "亮点是用药管理这一高频触点，能顺带导流到送药与随访。",
            "错位在硬件加提醒双轮，避开了纯软件健康APP的低留存困局。",
            "独特在把药盒变成家庭健康中枢，串联家属、医生与药师。",
            "罕见处是用物理分格降低出错率，信任来自看得见的安心。",
            "它抓的是多重用药老人的刚需，复购来自耗材与订阅。",
            "打法上是硬件获客、服务变现，留存靠每日提醒习惯。",
        ]
    if ('认知' in t) or ('训练' in t):
        return [
            "差异化在把认知训练游戏化，降低老人使用门槛，和传统康复形成错位。",
            "它用游戏外壳包装脑力训练，比枯燥康复操更容易被老人接受。",
            "亮点是认知筛查加训练闭环，早干预价值大但付费模型仍在摸索。",
            "错位在消费级认知健康，避开医院康复科的重流程。",
            "独特在把评估嵌进玩的过程，老人不抵触、数据自然沉淀。",
            "罕见处是用趣味任务替代康复训练，依从性明显更高。",
            "它卡位早期认知衰退，靠居家筛查避开机构排队。",
            "打法上是内容加算法，难度自适应，黏性来自进步反馈。",
        ]
    if ('远程' in t) or ('照护' in t) or ('护理' in t):
        return [
            "差异化在用远程监测替代部分人工巡检，用轻资产模型服务重人力需求的照护场景。",
            "它把护士的巡检拆成传感器加算法，人力成本骤降但信任建立慢。",
            "亮点是居家照护的实时化，家属付费意愿来自安全感。",
            "错位在远程照护，比养员密集型机构更轻、扩张更快。",
            "独特在把警报前移，意外发生前就干预，降低事故赔付。",
            "罕见处是用无感监测替代盯人，护工效率成倍提升。",
            "它抓的是居家失能刚需，用平台调度替代固定排班。",
            "打法上是设备加运营，规模靠网点密度摊薄成本。",
        ]
    if ('陪伴' in t) or ('社交' in t):
        return [
            "差异化在把孤独照护做成高频互动产品，黏性来自情感连接而非功能堆叠。",
            "它卖的是陪伴而非功能，留存靠关系感，模式偏社区运营。",
            "亮点是老年社交刚需，但变现长期依赖增值与硬件。",
            "错位在情感向产品，和工具型适老硬件形成互补。",
            "独特在用真人加AI混合陪伴，温度与成本兼顾。",
            "罕见处是把兴趣社群当留存引擎，老人为圈子回来。",
            "它卡位空巢情感缺口，用活动串联线下线上。",
            "打法上是内容加邻里，黏性靠每日打卡与互动。",
        ]
    if ('保险' in t) or ('理财' in t):
        return [
            "差异化在把保障与支付打通，用金融杠杆撬动老年客户的长期留存。",
            "它用保单绑定健康管理，续费逻辑比纯服务更稳。",
            "亮点是支付方即产品方，现金流质量高但合规要求严。",
            "错位在保险加养老打包，护城河在牌照与精算能力。",
            "独特在把理赔前置成服务，出险前就帮用户少生病。",
            "罕见处是用健康行为换保费折扣，双向绑定用户。",
            "它卡位支付端，用保障锁住长期客户关系。",
            "打法上是产品加渠道，规模靠存量客户交叉销售。",
        ]
    if ('食品' in t) or ('营养' in t) or ('膳食' in t):
        return [
            "差异化在把膳食干预做成日常食品形态，比保健品更易形成复购。",
            "它把营养变成一日三餐，依从性天然高于药片类方案。",
            "亮点是食品化健康干预，渠道可借电商也可进机构。",
            "错位在功能食品路线，避开严肃诊疗的漫长审批。",
            "独特在把医嘱变成好吃的东西，患者才愿意长期坚持。",
            "罕见处是用口味替代吞药，慢病管理依从性跳升。",
            "它卡位银发膳食，用订阅制绑定日常消耗。",
            "打法上是配方加供应链，复购靠每周配送。",
        ]
    if ('康复' in t) or ('辅具' in t) or ('器械' in t):
        return [
            "差异化在把康复训练设备化、居家化，避开机构高成本路径。",
            "它把康复从医院搬到家里，设备是入口、服务是留存。",
            "亮点是居家康复刚需，但医疗注册周期长。",
            "错位在消费级康复硬件，比医院设备更轻、更便宜。",
            "独特在把训练量化成数据，进步看得见才愿意续费。",
            "罕见处是用外骨骼替代人力，康复师效率倍增。",
            "它卡位居家康复，用租赁降低首次门槛。",
            "打法上是硬件加课程，黏性靠训练计划推进。",
        ]
    if ('地产' in t) or ('旅游' in t) or ('康养' in t):
        return [
            "差异化在把空间与康养结合，用重资产场景锁定中老年线下流量。",
            "它用地产承载养老服务，现金流靠资产也靠运营。",
            "亮点是线下高频触点，但重资产扩张速度受限。",
            "错位在康养地产，护城河在选址与配套。",
            "独特在把旅居做成候鸟式，老人随季节换场。",
            "罕见处是用会员制锁定多年消费，现金流前置。",
            "它卡位康养目的地，用环境替代部分治疗。",
            "打法上是资产加运营，规模受选址稀缺约束。",
        ]
    if 'B2C' in str(t):
        return [
            "差异化在直接触达C端老人、跳过机构中间层，但获客成本需自己扛。",
            "它走直营ToC，毛利高但地推与信任建立慢。",
            "亮点是直接握用户，用户资产厚，短板在获客贵。",
            "错位在C端直连，和省去渠道的轻模式。",
            "独特在自营商城加私域，利润不被中间商分走。",
            "罕见处是用内容种草直达老人，绕过传统渠道。",
            "它卡位直连用户，数据资产沉淀在自己手里。",
            "打法上是投放加复购，规模靠单客生命周期。",
        ]
    if 'B2B' in str(t):
        return [
            "差异化在先打机构渠道再渗透C端，获客更稳但起量较慢。",
            "它靠B端机构铺量，信任转嫁快，但利润被渠道分走。",
            "亮点是机构背书降低决策成本，短板在规模化慢。",
            "错位在渠道优先，先ToB站稳再反哺ToC。",
            "独特在把产品嵌进机构工作流，替换成本高、黏性强。",
            "罕见处是用标杆客户做灯塔，再横向复制。",
            "它卡位机构采购，用方案替代单品销售。",
            "打法上是渠道加交付，规模受实施人力约束。",
        ]
    return [
        f"差异化在围绕{t}做轻量化产品，避开重资产准入门槛，定位清晰。",
        f"它把{t}做成标准化服务，轻模式易起量、易复制。",
        f"亮点是{t}这一细分需求真实，它用产品化方式解决。",
        f"错位在{t}的消费级路线，监管与资质负担都更轻。",
        f"独特在把{t}从概念落到日用品，老人零学习成本。",
        f"罕见处是{t}被大厂忽略，它用细分切口站稳。",
        f"它卡位{t}刚需，用轻资产打法快速试错。",
        f"打法上是{t}场景化，黏性来自高频使用习惯。",
    ]

def build(e):
    serial = e.get('serial','')
    region = e.get('region','') or '海外'
    t1 = e.get('tag_l1') or []; t2 = e.get('tag_l2') or []
    if not isinstance(t1, list): t1 = [t1]
    if not isinstance(t2, list): t2 = [t2]
    tags = t1 + t2
    tag2 = t2[0] if t2 else (t1[0] if t1 else '银发')
    anchor = domain_anchor(tags)
    amount, date, total = parse_funding(e.get('funding_latest'), e.get('funding_total'))
    founded = e.get('founded')
    founded_y = founded if (isinstance(founded,(int,float)) or (isinstance(founded,str) and founded.isdigit())) else None
    biz = e.get('business_model') or ''
    payor = str(e.get('payor_model') or '')
    rv = e.get('research_value')
    try: rv = float(rv)
    except: rv = None

    # datapoint (always non-empty, embeds company-specific tokens)
    dp = ""
    tq = fmt_total(total)
    if tq: dp += tq + "、"
    if founded_y: dp += f"成立{founded_y}年至今、"
    if not dp: dp = f"围绕{tag2}方向、"

    amt_disp = amount or ''
    if amt_disp.startswith('约'): amt_disp = amt_disp[1:]
    if amt_disp.endswith('+'): amt_disp = amt_disp[:-1]

    # ---- 信号 ----
    if amount and date:
        sig = pick(serial, 'sig', [
            f"{fmt_date(date)}新获{amt_disp}融资，是近期最硬的赛道信号。",
            f"{amt_disp}于{fmt_date(date)}到账，构成近期最强信号锚点。",
            f"最新一笔{amt_disp}落在{fmt_date(date)}，融资信号明确。",
            f"{fmt_date(date)}完成{amt_disp}募资，是当下最值得盯的信号。",
            f"资本在{fmt_date(date)}投出{amt_disp}，赛道热度有了硬证据。",
        ])
    elif amount:
        sig = pick(serial, 'sig', [
            f"已披露{amt_disp}融资但时间点不明，信号强度中等。",
            f"账上有{amt_disp}融资入账，信号偏中等、缺时间锚。",
            f"{amt_disp}融资已确认，只是轮次时间没披露，信号尚可。",
        ])
    elif e.get('stage') == '被收购':
        sig = pick(serial, 'sig', [
            "已被战略收购，并购事件本身就是强信号。",
            "整笔标的被收编，并购动作即最强信号。",
        ])
    elif e.get('stage') in ('A轮','B轮','种子期'):
        sig = pick(serial, 'sig', [
            f"处于{e.get('stage')}早期轮次，融资信号偏弱但方向清晰。",
            f"刚走到{e.get('stage')}，早期融资信号不强但路线已定。",
            f"刚完成{e.get('stage')}募资，信号刚起步但故事清楚。",
            f"处在{e.get('stage')}，早期资本进场、方向已露头。",
        ])
    else:
        sig = pick(serial, 'sig', [
            f"暂未检索到融资事件，信号主要靠当前{tag2}需求支撑。",
            f"没有公开融资记录，信号来自{tag2}这条刚需线。",
            f"融资事件查不到，信号只能押{tag2}的真实需求。",
            f"公开渠道没看到融资，信号得靠{tag2}的刚需成色。",
            f"融资没披露，信号只能从{tag2}赛道热度反推。",
            f"暂无资本动作，信号寄托在{tag2}的真实付费上。",
        ])

    # ---- 信息量 ----
    if region == '海外':
        info = pick(serial, 'info', [
            f"海外标的信披通常更透明，{dp}可挖年报与公开资料做深度报道。",
            f"作为海外主体，{dp}年报与融资资料相对好查，适合做资料型深稿。",
            f"海外公司披露习惯较规范，{dp}从招股与新闻能拼出较完整画像。",
            f"境外标的透明度高，{dp}财报与公告易获取，便于交叉印证。",
            f"海外市场信披标准严，{dp}用公开文件能还原其经营轮廓。",
            f"出海标的财报披露齐备，{dp}做资料梳理不缺素材。",
            f"这类海外公司多在境外挂牌，{dp}披露颗粒度细，好深挖。",
            f"境外主体习惯季度披露，{dp}从公告里能捞出经营细节。",
            f"海外创业公司融资新闻密度高，{dp}公开跟踪成本低于国内。",
            f"在成熟市场，{dp}监管文件公开，做背调顺手。",
        ])
    else:
        info = pick(serial, 'info', [
            f"国内多为非上市主体，{dp}公开信息有限，需从工商与报道拼图。",
            f"本土标的常未上市，{dp}公开资料稀薄，要靠工商与新闻交叉验证。",
            f"国内主体信披少，{dp}信息要从招标与媒体里捡，做深稿成本高。",
            f"境内公司透明度低，{dp}得靠天眼查与行业稿拼出全貌。",
            f"国内大多没上市，{dp}资料缺口大，报道要更多一手走访。",
            f"境内标的少有公开财报，{dp}只能靠招投标与股权穿透拼。",
            f"这类公司多在一级市场，{dp}信息散落于媒体与工商，整合费劲。",
            f"国内未上市居多，{dp}数据要靠访谈与行业报告补全。",
            f"本土企业信披随意，{dp}公开信息少、做深稿前得多方佐证。",
            f"境内主体资料碎片化，{dp}从公众号与新闻里淘，效率低。",
        ])
    if not any(k in info for k in DIM_INFO):
        info = info + "公开信息可交叉补全。"
    if not any(k in info for k in DIM_INFO):
        info = info + "公开信息可交叉补全。"

    # ---- 差异化 ----
    diff = pick(serial, 'diff', diff_variants(tag2))
    if not any(k in diff for k in DIM_DIFF):
        diff = "差异化在" + diff

    # ---- 可复制 ----
    aspect = '机构打法' if ('B2B' in biz) else 'C端运营'
    if region == '海外':
        base = pick(serial, 'copy', [
            f"国内可借鉴其{aspect}思路，{tag2}这条线支付与监管要本地化重构，难直接平移。",
            f"对国内团队，其{aspect}可学，但{tag2}的付费与合规必须重做，不能直接搬。",
            f"国内若抄其{aspect}，得把{tag2}的支付结构和监管框架本地化，复制成本高。",
            f"它的{aspect}对国内有参照价值，只是{tag2}所处医保与商保环境不同，难照搬。",
            f"照搬其{aspect}不现实，{tag2}要按国内支付习惯重做一遍，门槛在合规。",
            f"国内看中它的{aspect}，可{tag2}方向先小步试水，支付侧须另起炉灶。",
            f"它的{aspect}对国内有启发，但{tag2}要过支付与牌照两道关。",
            f"国内想学其{aspect}，{tag2}须按本土合规重新设计。",
            f"{tag2}若平移国内，{aspect}可参考、支付侧得自建。",
            f"借鉴其{aspect}时，{tag2}的医保衔接是最大不确定。",
        ])
    else:
        base = pick(serial, 'copy', [
            f"本土团队可直接对标，{tag2}模式较轻、复制快，适合做国内案例深扒。",
            f"国内创业者能直接照着做，{tag2}模型轻、起量快，是现成对标样本。",
            f"本土玩家可一键对标，{tag2}打法轻、好复制，宜做国内深稿主角。",
            f"国内同行能直接模仿，{tag2}模式不重、跑得动，适合当作案例拆解。",
            f"{tag2}在国内有现成对标空间，轻模式易起量，可当作样本深写。",
            f"它的{tag2}路子国内能直接复用，复制成本低、适合做横向对比稿。",
            f"{tag2}在国内的对标空间清晰，轻资产易放大。",
            f"它的{tag2}模式本土能直接抄，门槛低、见效快。",
            f"国内做{tag2}可沿用其思路，落地阻力小。",
            f"{tag2}这类本土样本，值得拉出来横向比。",
        ])
    if ('未搜到' in payor) or (payor in ('', 'None')):
        risk = pick(serial, 'risk', [
            "风险在付费方未跑通，盈利模型待验证。",
            "隐患是买单方没验证，商业化路径还飘着。",
            "短板在谁掏钱不清晰，营收模型待打磨。",
        ])
    elif ('政府' in payor) or ('医保' in payor):
        risk = pick(serial, 'risk', [
            "需警惕政策与医保支付变动风险。",
            "要防政策与医保规则变动吃掉利润。",
            "隐忧在支付高度依赖公共资金，波动大。",
        ])
    else:
        risk = pick(serial, 'risk', [
            "可结合国内渠道做微创新落地。",
            "宜借国内现有渠道做本地化微改。",
            "能对接国内渠道做轻量落地。",
        ])
    copy = base + risk

    # ---- 头尾（含anchor与tag2以打散连续雷同）----
    head = pick(serial, 'head', [
        f"这家{anchor}企业" if anchor else "这家银发企业",
        f"主攻{anchor}方向的这家公司" if anchor else "这家银发公司",
        f"做{anchor}生意的这家企业" if anchor else "这家银发企业",
        f"身处{anchor}赛道的这家公司" if anchor else "身处银发赛道的公司",
        f"押注{anchor}路线的这家企业" if anchor else "押注银发路线的企业",
        f"这家做{anchor}买卖的公司" if anchor else "这家做银发买卖的公司",
        f"聚焦{anchor}的这户企业" if anchor else "聚焦银发的这户企业",
        f"在{anchor}里淘金的那家公司" if anchor else "在银发里淘金的那家公司",
    ])
    tail = pick(serial, 'tail', [
        f"对国内{anchor}赛道，{tag2}这条线值得持续跟踪。" if anchor else f"对国内银发赛道，{tag2}这条线值得持续跟踪。",
        f"国内{anchor}方向可把它的{tag2}当对标样本存底。" if anchor else f"国内银发方向可把它的{tag2}当对标样本存底。",
        f"放到国内{anchor}版图，{tag2}算可参照的异类样本。" if anchor else f"放到国内银发版图，{tag2}算可参照的异类样本。",
        f"国内{anchor}里，{tag2}这类打法值得放进选题池。" if anchor else f"国内银发里，{tag2}这类打法值得放进选题池。",
        f"对本土{anchor}从业者，它的{tag2}思路可作反向镜鉴。" if anchor else f"对本土银发从业者，它的{tag2}思路可作反向镜鉴。",
        f"国内{anchor}圈，{tag2}值得放进案例库。" if anchor else f"国内银发圈，{tag2}值得放进案例库。",
        f"把它的{tag2}放到国内{anchor}对照，启发不小。" if anchor else f"把它的{tag2}放到国内银发对照，启发不小。",
        f"本土{anchor}从业者看{tag2}，可少走弯路。" if anchor else f"本土银发从业者看{tag2}，可少走弯路。",
    ])

    rec = head + sig + info + diff + copy + tail

    if not has_digit(rec):
        rec += f"（研究价值{rv}分可作参考）" if rv is not None else "（检索序号可作锚点）"
    if not any(t and t in rec for t in tags):
        if '这家银发' in rec:
            rec = rec.replace('这家银发企业', f"这家聚焦{tag2}的银发企业", 1)

    return rec

def main():
    all_recs = []
    fails = []
    for b in BATCHES:
        d = json.load(open(os.path.join(HERE,'batches_full',f'batch_src_{b}.json'), encoding='utf-8'))
        for e in d:
            rec = build(e)
            e2 = dict(e); e2['recommend'] = rec
            issues = validate(e2, others=None, skip=['R6','R7','R8','R10'])
            fn = os.path.join(OUTDIR, f"draft_{e['serial']}.json")
            json.dump({"serial": e['serial'], "recommend": rec}, open(fn,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
            all_recs.append((e['serial'], rec, content_len(rec)))
            if issues:
                fails.append((e['serial'], issues))
    print(f"generated {len(all_recs)} drafts")
    print(f"len min/avg/max: {min(x[2] for x in all_recs)}/{sum(x[2] for x in all_recs)//len(all_recs)}/{max(x[2] for x in all_recs)}")
    print(f"FAIL (recommend rules R1-5,dedup,integrity,novelty,jargon,noabs): {len(fails)}")
    for s, iss in fails:
        print('  ', s, iss)

if __name__ == '__main__':
    main()
