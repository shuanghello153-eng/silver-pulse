import json

# 词表
tag_l2_vocab = set()
for cat, tags in {
"养老服务":["CCRC","SDOH","专业护理","中医养生","养老机构","安宁疗护","家政","居家医疗","居家康复","居家护理","康养地产","康复医疗","心理健康","慢病管理","护士上门","护士派遣","护工培训","护工平台","护理协调","殡葬","照护支持","认知症","认知筛查","认知训练","诊所","远程医疗","远程护理","适老化","陪诊"],
"康复辅具":["人形机器人","助听器","助行器","医疗器械","可穿戴监测","外骨骼","康复器械","护理床","智能药盒","机器人","用药提醒","用药管理","睡眠监测","紧急呼叫","跌倒监测","轮椅"],
"消费品":["个人护理","体检筛查","尿失禁","心血管","智能家居","智能硬件","更年期","服装鞋帽","电商","眼镜","纸尿裤","美妆护肤","药品","药品配送","视觉辅助","长寿抗衰","零售"],
"文娱社交":["健身","兴趣社群","就业","教育","文娱","旅游","相亲","短视频","社区","邻里社交","陪伴服务","陪伴机器人"],
"食品营养":["个性化营养","保健品","养老膳食","功能性食品","糖尿病","维生素矿物质","膳食补充剂","膳食配送","营养食品"],
"行业服务":["AI医疗","养老信息平台","养老咨询","养老软件","行业媒体","行业研究","资讯门户"],
"金融保险":["保险","保险科技","遗产规划","金融理财","长护险"],
"投资机构":["VC","产业基金","养老REIT"],
}.items():
    tag_l2_vocab.update(tags)

data = [
{"name":"浙江三网科技股份有限公司","tag_l2":["养老信息平台","适老化"],"confidence":"med","note":"未来社区数字化运营+AI系统+适老化产品，偏平台与适老产品"},
{"name":"云中漫步（上海）机器人科技有限公司","tag_l2":["养老信息平台"],"confidence":"med","note":"社区养老滴滴模式，提供平台撮合；名含机器人但描述未提具体机器人产品"},
{"name":"深圳艺心灵文化传媒有限公司","tag_l2":["行业媒体"],"confidence":"high","note":"自媒体提供流量"},
{"name":"上海青浦区艾芙老人家服务中心","tag_l2":["居家护理"],"confidence":"med","note":"居家养老，提供居家资源"},
{"name":"辽阳市白塔区百善居家和社区养老服务中心","tag_l2":["养老膳食"],"confidence":"high","note":"社区共享食堂"},
{"name":"上海企派派科技有限公司","tag_l2":["养老软件","家政"],"confidence":"high","note":"家政养老派单系统"},
{"name":"安徽哈工智能科技有限公司","tag_l2":["护理床"],"confidence":"high","note":"智能护理床产品（名含机器人但提供病床/护理床）"},
{"name":"湖南安瑜健康科技有限公司","tag_l2":["养老软件","可穿戴监测"],"confidence":"med","note":"居家养老系统+手表(可穿戴)"},
{"name":"谢红家政服务部","tag_l2":["家政"],"confidence":"low","note":"仅'有团队/团队长'，据名称判断为家政"},
{"name":"北京大兴国际商业服务有限公司","tag_l2":["康养地产"],"confidence":"low","note":"园区运营公司，提供政策及办公免租，最接近康养地产/园区载体"},
{"name":"温州职业技术学院","tag_l2":["行业研究","适老化"],"confidence":"med","note":"智慧养老空间设计研究+学术调研数据分析"},
{"name":"山海岛滋补行","tag_l2":["保健品"],"confidence":"med","note":"藏区滋补养生产品"},
{"name":"联众昌","tag_l2":["保健品"],"confidence":"low","note":"仅'大健康/市场'，需求药食同源产品，据需求猜保健品/功能性食品"},
{"name":"重庆经纬","tag_l2":["康复器械"],"confidence":"med","note":"康养设备销售/维护/租赁/运营"},
{"name":"山西尧望旅行社有限公司","tag_l2":["旅游"],"confidence":"high","note":"银发客户精品小包团定制旅游"},
{"name":"数百年科技有限公司","tag_l2":["服装鞋帽"],"confidence":"med","note":"防护穿着产品"},
{"name":"北京寿山福海养老集团","tag_l2":["养老机构"],"confidence":"high","note":"运营多家五星级养老机构"},
{"name":"唐派集团","tag_l2":["医疗器械","康复器械"],"confidence":"high","note":"家庭医疗器械+康复辅具(适老产品)"},
{"name":"开开华彩","tag_l2":["教育"],"confidence":"high","note":"中老年课程"},
{"name":"兰州机场佰翔酒店","tag_l2":["康养地产"],"confidence":"med","note":"酒店+旅居养老资源，最接近康养地产载体"},
{"name":"海南佰唯基因生物科技有限公司","tag_l2":["康复医疗"],"confidence":"low","note":"干细胞/再生医学医院，词表无精确词，取再生医学最接近康复医疗"},
{"name":"太平洋人寿","tag_l2":["保险"],"confidence":"high","note":"保险公司"},
{"name":"浙江澎城智能","tag_l2":["AI医疗","养老软件"],"confidence":"med","note":"养老AI接口+医院AI智能体落地"},
{"name":"北京中经城投（北京）健康管理有限公司","tag_l2":["护工培训"],"confidence":"high","note":"护理员职业培训学校"},
{"name":"海南东方柏嘉酒店管理公司","tag_l2":["康养地产"],"confidence":"med","note":"康养主题连锁酒店+旅居管家"},
{"name":"无锡市第二人民医院","tag_l2":["诊所"],"confidence":"med","note":"综合医院老年科，取最接近医疗机构'诊所'"},
{"name":"杉木","tag_l2":["陪诊"],"confidence":"low","note":"高端医疗绿通/干细胞，取最接近'陪诊'(绿通)"},
{"name":"迈纽康人工智能科技(上海)有限公司（迈纽康人工智能科技(四川)运营中心）","tag_l2":["医疗器械","AI医疗"],"confidence":"med","note":"医疗级无创体测AI设备"},
{"name":"四川福孝家养老服务有限公司","tag_l2":["养老机构","居家护理"],"confidence":"high","note":"社区养老机构+居家服务"},
{"name":"万企成（重庆）健康科技有限公司","tag_l2":["社区"],"confidence":"low","note":"康养社区服务站，据描述猜'社区'"},
{"name":"成都莲荷广告传媒有限公司","tag_l2":["智能硬件","紧急呼叫"],"confidence":"med","note":"老年室内外安全用品/呼救器"},
{"name":"山东泉辉养老产业发展有限公司","tag_l2":["养老机构"],"confidence":"med","note":"220张床位线下实体"},
{"name":"长沙湘粤医药科技有限公司","tag_l2":["长寿抗衰"],"confidence":"med","note":"抗衰长寿相关产品+全病程管理"},
{"name":"谷川联行","tag_l2":["养老咨询"],"confidence":"med","note":"协助企业获取政策+招商对接"},
{"name":"河南瑞阳医康养集团有限公司","tag_l2":["养老机构","居家护理"],"confidence":"high","note":"养老院+社区+居家+中医馆"},
{"name":"三河市西金商贸有限公司","tag_l2":["零售"],"confidence":"med","note":"中老年用品+客户群体，商贸零售"},
{"name":"成都氢饮科技有限公司","tag_l2":["功能性食品"],"confidence":"med","note":"富氢水/药食同源健康饮品"},
{"name":"弘康人寿","tag_l2":["保险","遗产规划"],"confidence":"high","note":"保险+财富传承(遗产规划)+康养绿通"},
{"name":"广州康特莱科技有限公司","tag_l2":["保健品","远程医疗"],"confidence":"med","note":"医药保健+互联网医疗(远程医疗)"},
{"name":"江西哦咔科技有限公司","tag_l2":["养老机构"],"confidence":"med","note":"社区养老院"},
{"name":"广能(广州)规划设计公司","tag_l2":["养老咨询"],"confidence":"med","note":"医养结合规划设计开发"},
{"name":"北京梵霖未来科技有限公司","tag_l2":["陪伴机器人"],"confidence":"high","note":"情感陪伴机器人+养老数字人"},
{"name":"上海云虚互伴科技有限公司","tag_l2":["陪伴服务"],"confidence":"med","note":"AI数字人陪聊"},
{"name":"太素方舟（北京）生物科技","tag_l2":["养老机构"],"confidence":"med","note":"社区养老连锁加盟"},
{"name":"济南牧源羊乳","tag_l2":["营养食品"],"confidence":"med","note":"鲜羊奶酸奶营养品"},
{"name":"美适浴（上海）卫浴有限公司","tag_l2":["适老化"],"confidence":"med","note":"开门浴缸(适老卫浴)"},
]

out_path = "G:/workbuddy/2026-06-28-23-34-20/silver-pulse/.tmp/sd_results/sdr_1.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# ---- 校验 ----
errors = []
assert len(data) == 46, f"条数错误: {len(data)}"
names = [d["name"] for d in data]
assert len(names) == len(set(names)), f"存在重复name: {[n for n in names if names.count(n)>1]}"
for d in data:
    for t in d["tag_l2"]:
        if t not in tag_l2_vocab:
            errors.append(f"非法标签 {t} @ {d['name']}")
    assert len(d["tag_l2"]) >= 1, f"空标签 @ {d['name']}"
    assert d["confidence"] in ("high","med","low"), f"置信度非法 @ {d['name']}"

print("校验通过: 46条, 无重复name")
print("非法标签数:", len(errors))
for e in errors:
    print(e)

from collections import Counter
c = Counter(d["confidence"] for d in data)
print("置信度分布:", dict(c))
print("low条目:", [d["name"] for d in data if d["confidence"]=="low"])
