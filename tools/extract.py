import pymupdf, re, json, os, time
from pypinyin import lazy_pinyin, Style
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('MEDPRICE_PDF', os.path.join(ROOT,'data','doc.pdf'))
if not os.path.exists(SRC):
    SRC='/home/sora/Documents/2024年6月版《成都市医疗服务项目价格汇编（2024版）》.pdf'
doc=pymupdf.open(SRC)
code15=re.compile(r'^\d{15}$')
han=re.compile(r'[一-鿿]')

# ---- 分类：数字前缀=编码前2位；字母前缀按文档「位置」归入所处的数字分类，末尾附录段归「其他项目」----
import bisect
MAJORS={1:"综合医疗服务类",2:"医技诊疗类",3:"临床诊疗类",4:"中医及民族医诊疗类",5:"其他项目"}
# 名称取自 PDF 各大类「本类说明：…包括 A、B、…」原文（未改动措辞）
SUBCATS=[
  ("11","一般医疗服务",1),("12","一般检查治疗",1),("13","社区卫生及预防保健项目",1),("14","其它医疗服务项目",1),
  ("21","医学影像",2),("22","超声检查",2),("23","核医学",2),("24","放射治疗",2),("25","检验",2),("26","血型与配血",2),("27","病理检查",2),
  ("31","临床各系统诊疗",3),("32","经血管介入诊疗",3),("33","手术治疗",3),("34","物理治疗与康复",3),
  ("41","中医外治",4),("42","中医骨伤",4),("43","针刺",4),("44","灸法",4),("45","推拿疗法",4),("46","中医肛肠",4),("47","中医特殊疗法",4),("48","中医综合",4),("49","民族医诊疗",4),
  ("50","其他项目",5),
]
APPENDIX="50"
SUB_SET={c for c,_,_ in SUBCATS}
CATEGORIES=[{"code":c,"name":n,"major":mj,"major_name":MAJORS[mj]} for c,n,mj in SUBCATS]
# 数字分类的页码区间（正文顺序）在收集完项目后计算；此处占位
NUM_START=[]   # [(start_page, code), ...] 升序
APPX_START=[10**9]
def cat_of(local_code, page_no):
    p=(local_code or "")[:2]
    if p in SUB_SET and p!=APPENDIX: return p          # 数字编码直接归类
    # 字母编码：按文档位置
    if page_no>=APPX_START[0]: return APPENDIX          # 末尾附录段 → 其他项目
    i=bisect.bisect_right([s for s,_ in NUM_START], page_no)-1
    return NUM_START[i][1] if i>=0 else NUM_START[0][1]
def clean(s): return (s or '').replace('\n','').strip()
def only_han(s): return ''.join(han.findall(s or ''))
def py_full(s):
    s=only_han(s); return ''.join(lazy_pinyin(s)) if s else ''
def py_init(s):
    s=only_han(s); return ''.join(lazy_pinyin(s, style=Style.FIRST_LETTER)) if s else ''
def toPt(b):
    # 高亮框以 PDF 点坐标存储（原点左上）：[x, y, w, h]，前端按 pdf.js 视口 scale 叠加
    if not b: return None
    x0,y0,x1,y1=b
    return [round(x0,1), round(y0,1), round(x1-x0,1), round(y1-y0,1)]

items=[]; page_dims={}; t0=time.time()
for pno in range(doc.page_count):
    page=doc[pno]
    tabs=page.find_tables()
    if not tabs.tables: continue
    got=False
    for t in tabs.tables:
        textrows=t.extract(); rowobjs=t.rows
        for tr, ro in zip(textrows, rowobjs):
            if len(tr)<13: continue
            c=[clean(x) for x in tr]
            if not code15.match(c[0]): continue
            name=c[3] or c[1]
            cells=getattr(ro,'cells',None) or []
            hl=[]
            rb=toPt(getattr(ro,'bbox',None))
            if rb: hl.append({"x":rb[0],"y":rb[1],"w":rb[2],"h":rb[3],"k":"row"})
            if len(cells)>3:
                nb=toPt(cells[3])
                if nb: hl.append({"x":nb[0],"y":nb[1],"w":nb[2],"h":nb[3],"k":"name"})
            for ci in range(8,13):
                if ci<len(cells):
                    pb=toPt(cells[ci])
                    if pb: hl.append({"x":pb[0],"y":pb[1],"w":pb[2],"h":pb[3],"k":"price"})
            items.append({
              "national_code":c[0],"national_name":c[1],"local_code":c[2],"name":name,
              "connotation":c[4],"exclusion":c[5],"unit":c[6],"note":c[7],
              "prices":[c[8],c[9],c[10],c[11],c[12]],"remark":c[13] if len(c)>13 else "",
              "page_no":pno+1,
              "py":py_full(name),"init":py_init(name),
              "npy":py_full(c[1]),"ninit":py_init(c[1]),
              "hl":hl,
            })
            got=True
    if got:
        r=page.rect; page_dims[str(pno+1)]=[round(r.width,1), round(r.height,1)]

seen=set(); uniq=[]
for it in items:
    k=(it["national_code"], it["local_code"], it["name"])
    if k in seen: continue
    seen.add(k); uniq.append(it)

# ---- 计算数字分类页码区间与附录起点，再给每个项目定位分类 ----
num_min={}; num_max=0
for it in uniq:
    p2=it["local_code"][:2]
    if p2 in SUB_SET and p2!=APPENDIX:
        num_min[p2]=min(num_min.get(p2,10**9), it["page_no"])
        num_max=max(num_max, it["page_no"])
NUM_START[:] = sorted((pg,code) for code,pg in num_min.items())
APPX_START[0] = num_max+1        # 数字分类之后（末尾附录段）→ 其他项目
for it in uniq:
    it["cat"]=cat_of(it["local_code"], it["page_no"])
print("NUM_START:", NUM_START[:3], "... APPX_START:", APPX_START[0])

out={"version_label":"2024版",
     "source_file":"2024年6月版《成都市医疗服务项目价格汇编（2024版）》.pdf",
     "pdf_file":"doc.pdf",
     "coord":"pt",                       # 高亮框坐标单位：PDF 点
     "price_levels":["三甲","三乙","二甲","二乙","二乙以下"],
     "page_count":doc.page_count,
     "categories":CATEGORIES,
     "items":uniq,"page_dims":page_dims}
os.makedirs(os.path.join(ROOT,'data'), exist_ok=True)
s=json.dumps(out, ensure_ascii=False)
open(os.path.join(ROOT,'data','proto_data.json'),'w',encoding='utf-8').write(s)
print("items:", len(uniq), "pages_with_items:", len(page_dims), "of", doc.page_count,
      "time %.0fs"%(time.time()-t0), "json %.1fMB"%(len(s.encode('utf-8'))/1048576))
print("sample:", uniq[0]["name"], "page", uniq[0]["page_no"], "hl", len(uniq[0]["hl"]), "dims", page_dims[str(uniq[0]["page_no"])])
