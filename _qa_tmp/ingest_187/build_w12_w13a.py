# -*- coding: utf-8 -*-
"""主AI亲自起草 W12(11家日本介护) + W13_A(1家德国长寿诊所) 的入库记录。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

def rec(**kw):
    base = {
        "serial": "", "name": "", "name_cn": "", "region": "海外",
        "country_hint": "", "website_url": "", "crunchbase_url": "",
        "description": "", "recommend": "", "tag_l2": [], "tag_l1": [],
        "payor_model": "", "funding_latest": {}, "funding_total": {"amount": "未披露", "display": "未披露"},
        "investors": ["未搜到"], "stage": "", "founded": "未搜到",
        "info_score": 0.0, "diff_score": 0.0, "copy_score": 0.0,
        "source": "外部AI名单入库(W12_企业_2026-07-25) 2026-07-26",
        "ingest_time": "2026-07-26", "update_time": "2026-07-26",
        "deep_article_links": [], "_status_raw": "", "_note_raw": "",
    }
    base.update(kw)
    return base

def fl(date, amount, rnd, display):
    return {"date": date, "amount": amount, "round": rnd, "display": display}

w12 = [
    rec(
        name="ワタミ（Watami）", name_cn="和民", country_hint="日本",
        website_url="https://www.watami.co.jp/",
        description="日本大型综合餐饮与银发餐配企业，核心银发业务为『宅食』——每日向老年家庭配送约24万份定制餐，并在送餐时附带独居老人安全探视（見守り）；2015年已将旗下介护业务出售给SOMPO。收入来自餐食配送费与餐饮门店。",
        recommend="把老年助餐做成每天数十万份规模、并让送餐员顺带承担独居老人安全探视，这种'一餐两用'的组合在国内社区助餐刚起步的阶段很有参考价值；它早年剥离重资产介护、聚焦轻资产餐配的取舍，也说明了餐饮集团做老龄市场的另一条路径。国内老年助餐多为政府补贴驱动，商业化配送网络仍在早期，其单量密度与探视增值服务的搭法可供经营者参照。",
        tag_l2=["膳食配送", "养老膳食"], tag_l1=["食品营养"],
        payor_model="个人自费（餐食配送费）",
        funding_latest=fl("上市", "东证Prime上市(7522)", "IPO", "东证Prime上市 (代码7522)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=8.0, diff_score=6.0, copy_score=8.0,
        _status_raw="上市·现役", _note_raw="外食+介护（ワタミの介護）+宅食，IR 月次/适時披露；TSE Prime（介护业务2015年已售予SOMPO）",
    ),
    rec(
        name="ケア21（Care21）", name_cn="Care21", country_hint="日本",
        website_url="https://www.care21.co.jp/",
        description="以关西地区为主的介护服务运营商，提供访问介护、日间照料与收费养老院（有料老人ホーム），收入来自介护保险结算与自费服务费。",
        recommend="作为深耕单一区域的中型介护运营商，它展示了在人力密集、利润偏薄的上门与机构照护里，靠区域密度做出规模的活法；日本介护保险的结算机制与中国长护险高度相似，其人效控制与站点扩张节奏对国内区域型养老运营商有直接参照意义。",
        tag_l2=["养老机构", "居家护理"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("上市", "东证Standard上市(2373)", "IPO", "东证Standard上市 (代码2373)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=6.0, diff_score=4.0, copy_score=8.0,
        _status_raw="上市·现役", _note_raw="关西地盘介护事業者；TSE Standard",
    ),
    rec(
        name="チャーム・ケア・コーポレーション（Charm Care）", name_cn="Charm Care", country_hint="日本",
        website_url="https://www.charmcc.jp/",
        description="关西与关东布局的中高端收费养老院运营商，运营逾百处介护付有料老人ホーム，主打付费入住，收入来自入住金与月度介护服务费。",
        recommend="把介护付养老院做成持续开新店的成长型公司，这在低增长的日本养老业里并不多见，其中高端定位加密集展店的打法说明了付费养老在成熟市场依然能跑出成长性；国内高端养老社区多为重资产会员制，其偏租赁的轻资产扩张与坪效管理可供国内经营者参考。",
        tag_l2=["养老机构"], tag_l1=["养老服务"],
        payor_model="个人自费+介护保险",
        funding_latest=fl("上市", "东证Prime上市(6062)", "IPO", "东证Prime上市 (代码6062)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=6.0, diff_score=5.0, copy_score=7.0,
        _status_raw="上市·现役", _note_raw="介护付有料老人ホーム 101+ 据点；TSE Prime",
    ),
    rec(
        name="ウチヤマホールディングス（Uchiyama HD）", name_cn="内山控股", country_hint="日本",
        website_url="http://www.uchiyama-gr.jp/",
        description="多元控股集团，以介护事业（『さわやか倶楽部』全国逾120处设施）为核心，另有卡拉OK与餐饮业务；介护收入来自介护保险与入住费。",
        recommend="介护主业之外还并行卡拉OK与外食，这种把老年娱乐消费与照护装进同一集团的结构，反映了区域民营企业围绕老年人时间与消费做多元经营的思路；对国内想从单一养老服务向老年生活消费延伸的运营商来说，是一个现成的组合样本。",
        tag_l2=["养老机构"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("上市", "东证Standard上市(6059)", "IPO", "东证Standard上市 (代码6059)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=5.0, diff_score=5.0, copy_score=6.0,
        _status_raw="上市·现役", _note_raw="介护（さわやか倶楽部全国 120+ 设施）+卡拉OK/外食；TSE Standard",
    ),
    rec(
        name="フレアス（Fureasu）", name_cn="Fureasu", country_hint="日本",
        website_url="https://fureasu.jp/",
        description="以上门按摩（在宅マッサージ）起家的居家照护企业，扩展至看护小规模多机能与临终照护（hospice），服务居家及失能老人，收入来自医保/介护保险结算与自费。",
        recommend="从上门按摩这样一个细分切口进入居家照护，再叠加临终照护，这条'先做高频轻服务、再向重照护延伸'的路径颇有想法；国内上门康复、上门中医推拿正在兴起，其把可报销的上门理疗做成连锁、并向安宁疗护延伸的做法，对相关创业者有实操层面的启发。",
        tag_l2=["居家护理", "安宁疗护"], tag_l1=["养老服务"],
        payor_model="医保/介护保险+个人自费",
        funding_latest=fl("上市", "东证Growth上市(7062)", "IPO", "东证Growth上市 (代码7062)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=5.0, diff_score=7.0, copy_score=7.0,
        _status_raw="上市·现役", _note_raw="在宅按摩+看護小規模多機能+hospice；TSE Growth",
    ),
    rec(
        name="SOMPO HD", name_cn="SOMPO控股", country_hint="日本",
        website_url="https://www.sompo-hd.com/",
        description="日本大型保险控股集团，旗下SOMPOケア为日本头部介护运营商之一，形成保险与介护并行的业务结构，并推进照护数据与养老科技布局；收入以财险寿险为主，介护为增长板块。",
        recommend="一家财险巨头把介护养老纳入主业，用保险资金与客户资源支撑重资产照护，这种'保险公司自己下场做养老'的结构，正是国内险企布局康养时最常参照的路线；它如何在低回报的照护业务与保险主业之间做协同、沉淀照护数据，对国内保险系养老玩家有很强的参考意义。",
        tag_l2=["保险", "养老机构"], tag_l1=["金融保险", "养老服务"],
        payor_model="保险+介护保险+个人自费",
        funding_latest=fl("上市", "东证Prime上市(8630)", "IPO", "东证Prime上市 (代码8630)"),
        funding_total={"amount": "上市公司", "display": "上市公司"},
        stage="已上市", info_score=8.0, diff_score=6.0, copy_score=8.0,
        _status_raw="上市·现役", _note_raw="SOMPOケア母公司，东证 Prime；IR 资料 2026-05",
    ),
    rec(
        name="ベネッセホールディングス（Benesse HD）", name_cn="倍乐生控股", country_hint="日本",
        website_url="https://www.benesse.co.jp/",
        description="教育起家的综合服务集团，旗下ベネッセスタイルケア运营全国350余处收费养老院，为日本介护龙头之一；2024年经瑞典EQT与创始福武家族以约2080亿日元要约收购完成MBO，并从东证Prime退市。",
        recommend="教育巨头被海外基金联手创始家族私有化，退市后押注教育与长照两大主业转型，这类'成熟龙头借外部资本做深度重整'的案例，正是理解养老资产为何吸引长期资金的好切口；它把在教育领域积累的会员与品牌迁移到养老的路径，也给国内跨界做养老的企业提供了现实参照。",
        tag_l2=["养老机构"], tag_l1=["养老服务"],
        payor_model="个人自费+介护保险",
        funding_latest=fl("2024", "约2080亿日元", "MBO私有化", "EQT+福武家族 MBO 私有化退市 约2080亿日元 (2024)"),
        funding_total={"amount": "约2080亿日元收购", "display": "MBO私有化 约2080亿日元 (2024)"},
        investors=["EQT AB (BPEA Fund VIII)", "福武家族"],
        stage="已退市私有化", founded=1955, info_score=8.0, diff_score=7.0, copy_score=7.0,
        _status_raw="上市·现役（信源标注，实际2024已MBO退市，已更正）", _note_raw="ベネッセスタイルケア母公司，全国 350+ 有料老人ホーム运营；2024 EQT+福武家族 MBO 退市",
    ),
    rec(
        name="ニチイ学館（Nichii Gakkan）", name_cn="日医学馆", country_hint="日本",
        website_url="https://www.nichiigakkan.co.jp/",
        description="日本医疗事务外包与介护龙头，旗下『ニチイケア』运营大量居家与机构介护，并经营介护人才培训；2020年经贝恩资本主导MBO私有化退市，营收规模约2682亿日元。",
        recommend="医疗事务与介护双主业的老牌龙头被贝恩私有化，是海外基金重仓日本老龄资产的标志性一役；它同时握有介护服务与介护人才培训两端，这种'自己开店又自己培养护理员'的自供体系，对长期受困于护理员短缺的国内养老企业尤其有启发。",
        tag_l2=["养老机构", "护工培训"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("2020", "未披露", "MBO私有化", "贝恩资本主导 MBO 私有化退市 (2020)"),
        funding_total={"amount": "未披露", "display": "MBO私有化退市 (2020)"},
        investors=["Bain Capital"],
        stage="已退市私有化", info_score=7.0, diff_score=7.0, copy_score=8.0,
        _status_raw="已退市/私有化", _note_raw="2020 Bain Capital MBO 私有化退市；营收约2682亿日元；选题价值：PE 收购养老龙头",
    ),
    rec(
        name="メッセージ（Message）", name_cn="Message（现SOMPO Care Message）", country_hint="日本",
        website_url="https://www.message.co.jp/",
        description="曾为日本大型收费养老院运营商，2016–2017年被SOMPO（时为损保ジャパン日本興亜）收购并退市，整合为SOMPOケアメッセージ，成为SOMPO介护版图核心。",
        recommend="一家独立养老运营商最终被保险集团收编、成为对方介护主业的骨架，这条'被并购退出'的路径揭示了成熟市场里中型养老资产的常见归宿是产业资本整合；国内养老机构普遍面临规模不经济，其被险资吸收时的估值逻辑与整合方式有借鉴意义。",
        tag_l2=["养老机构"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("2017", "未披露", "被SOMPO收购", "被SOMPO收购退市 (2017)"),
        funding_total={"amount": "未披露", "display": "被SOMPO收购退市 (2017)"},
        investors=["SOMPO HD"],
        stage="已被收购", info_score=6.0, diff_score=6.0, copy_score=7.0,
        _status_raw="已退市/私有化", _note_raw="2017 被 SOMPO 收购退市（旧社名メッセージ→SOMPOケアメッセージ）",
    ),
    rec(
        name="ツクイ（Tsukui）", name_cn="Tsukui", country_hint="日本",
        website_url="https://www.tsukui.net/",
        description="日本规模领先的日间照料（デイサービス）服务商，兼营居家介护，全国站点网络庞大；2021年经MBK Partners要约收购非公开化退市，运营仍持续。",
        recommend="把日间照料这类相对标准化的介护服务做成全国最大网络，再被亚洲基金私有化，说明日托这种'轻资产、可复制、依赖介护保险结算'的模式在成熟市场具备规模与并购价值；国内社区日照中心多依赖补贴、盈利模型尚未跑通，其单店经济与连锁扩张经验很有参照价值。",
        tag_l2=["养老机构", "居家护理"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("2021", "未披露", "TOB私有化", "MBK Partners TOB 非公开化退市 (2021)"),
        funding_total={"amount": "未披露", "display": "TOB私有化退市 (2021)"},
        investors=["MBK Partners"],
        stage="已退市私有化", info_score=6.0, diff_score=5.0, copy_score=8.0,
        _status_raw="已退市/私有化", _note_raw="2021-06 MBK Partners TOB 非公開化退市；运营站仍活跃；并入W5以色列_B重复条",
    ),
    rec(
        name="セントケア・ホールディングス（Saint-Care）", name_cn="圣护控股", country_hint="日本",
        website_url="https://www.saint-care.com/",
        description="日本访问介护（上门介护）领先运营商，提供居家介护、访问看护与福祉用具等服务；2026年3月经股份合并挤出方式完成私有化退市。",
        recommend="上门介护龙头在2026年最新完成私有化，是观察日本居家照护赛道资本运作的新鲜案例；上门介护人力重、单值低，它能长期跑通并获得资本青睐，其排班效率与访问看护的搭配，对正在发力居家上门护理的国内企业是当下最具时效性的参照。",
        tag_l2=["居家护理", "护士上门"], tag_l1=["养老服务"],
        payor_model="介护保险+个人自费",
        funding_latest=fl("2026-03", "未披露", "私有化退市", "股份合并挤出私有化退市 (2026-03)"),
        funding_total={"amount": "未披露", "display": "私有化退市 (2026-03)"},
        stage="已退市私有化", info_score=6.0, diff_score=6.0, copy_score=8.0,
        _status_raw="已退市/私有化", _note_raw="2026-03-13 股票合并挤牌（5905149:1 squeeze-out）退市",
    ),
]

w13a = [
    rec(
        name="YEARS", name_cn="YEARS长寿预防诊所", country_hint="德国",
        website_url="https://years.health",
        source="外部AI名单入库(W13_A_企业_2026-07-25) 2026-07-26",
        description="德国柏林的高端长寿预防医疗机构，提供一日式深度体检——涵盖230余项生物标志物检测与全身MRI，并结合AI分析给出健康评估，套餐价约1900至16900欧元，直接面向注重健康与抗衰的消费者B2C直售。",
        recommend="把预防医学做成面向高净值人群的一次性高价体检产品，用海量生物标志物加影像加AI给出'长寿评估'，这种消费医疗定位在国内高端体检升级的语境下颇有想象空间；国内美年、慈铭等体检机构正寻求从筛查向健康管理与抗衰延伸，其产品化定价与高端获客方式提供了现成参照。",
        tag_l2=["长寿抗衰", "体检筛查"], tag_l1=["消费品"],
        payor_model="个人自费",
        funding_latest=fl("未披露", "未披露", "未披露", "未披露"),
        stage="成长期", info_score=5.0, diff_score=8.0, copy_score=7.0,
        _status_raw="现役·私营", _note_raw="柏林长寿预防诊所，一日式 230+ 生物标志物 + 全身 MRI + AI 综合体检，套餐 €1.9k–16.9k，B2C 直售；W13-A 唯一真银发经济企业",
    ),
]

json.dump(w12, open(os.path.join(HERE, "draft_out", "W12_ent_2026-07-25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(w13a, open(os.path.join(HERE, "draft_out", "W13_A_ent_2026-07-25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"W12 写入 {len(w12)} 家，W13_A 写入 {len(w13a)} 家")
