import pymupdf, re, json, os, time
from pypinyin import lazy_pinyin, Style
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('MEDPRICE_PDF', os.path.join(ROOT,'data','doc.pdf'))
if not os.path.exists(SRC):
    SRC='/home/sora/Documents/2024年6月版《成都市医疗服务项目价格汇编（2024版）》.pdf'
doc=pymupdf.open(SRC)
code15=re.compile(r'^\d{15}$')
han=re.compile(r'[一-鿿]')

# ---- 大项分类：正文中形如「一、综合医疗服务类」的一级标题（跳过前言页 1-6）----
import bisect
cat_pat=re.compile(r'^([一二三四五六七八九十]+)、\s*(.+?(?:类|项目))$')
cats=[]  # (start_page(1-based), title)
seen_title=set()
for pno in range(6, doc.page_count):
    for ln in doc[pno].get_text().splitlines():
        ln=ln.strip()
        m=cat_pat.match(ln)
        if m and len(ln)<=16:
            title=m.group(1)+'、'+m.group(2)
            if title not in seen_title:
                seen_title.add(title); cats.append((pno+1, title))
cats.sort()
CAT_STARTS=[c[0] for c in cats]
CATEGORIES=[{"no":i+1,"title":t,"start_page":p} for i,(p,t) in enumerate(cats)]
def cat_of(page_no):
    i=bisect.bisect_right(CAT_STARTS, page_no)-1
    return (i+1) if i>=0 else 0        # 1-based 大项序号，0=未归类
print("categories:", [(p,t) for p,t in cats])
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
              "catno":cat_of(pno+1),
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
