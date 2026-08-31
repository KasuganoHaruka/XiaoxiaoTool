import pymupdf, re, json, base64, os
from pypinyin import lazy_pinyin, Style
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.environ.get('MEDPRICE_PDF','/home/sora/Documents/2024年6月版《成都市医疗服务项目价格汇编（2024版）》.pdf')
DPI=110
S=DPI/72.0
doc=pymupdf.open(SRC)
PAGES=[10,14,15,17,18,20,23,24,30,40,120,500]
code15=re.compile(r'^\d{15}$')
han=re.compile(r'[一-鿿]')
def clean(s): return (s or '').replace('\n','').strip()
def only_han(s): return ''.join(han.findall(s or ''))
def py_full(s):
    s=only_han(s); return ''.join(lazy_pinyin(s)) if s else ''
def py_init(s):
    s=only_han(s); return ''.join(lazy_pinyin(s, style=Style.FIRST_LETTER)) if s else ''
def toPx(b):
    if not b: return None
    x0,y0,x1,y1=b
    return [round(x0*S,1), round(y0*S,1), round((x1-x0)*S,1), round((y1-y0)*S,1)]
items=[]; images={}; imgdim={}
for pno in PAGES:
    page=doc[pno]
    tabs=page.find_tables()
    if not tabs.tables: continue
    got=False
    for t in tabs.tables:
        textrows=t.extract()
        rowobjs=t.rows
        for tr, ro in zip(textrows, rowobjs):
            if len(tr)<13: continue
            c=[clean(x) for x in tr]
            if not code15.match(c[0]): continue
            name=c[3] or c[1]
            cells=getattr(ro,'cells',None) or []
            hl=[]
            rb=toPx(getattr(ro,'bbox',None))
            if rb: hl.append({"x":rb[0],"y":rb[1],"w":rb[2],"h":rb[3],"k":"row"})
            if len(cells)>3:
                nb=toPx(cells[3])
                if nb: hl.append({"x":nb[0],"y":nb[1],"w":nb[2],"h":nb[3],"k":"name"})
            for ci in range(8,13):
                if ci<len(cells):
                    pb=toPx(cells[ci])
                    if pb: hl.append({"x":pb[0],"y":pb[1],"w":pb[2],"h":pb[3],"k":"price"})
            rec={
              "national_code":c[0],"national_name":c[1],
              "local_code":c[2],"name":name,
              "connotation":c[4],"exclusion":c[5],"unit":c[6],"note":c[7],
              "prices":[c[8],c[9],c[10],c[11],c[12]],
              "remark":c[13] if len(c)>13 else "",
              "page_no":pno+1,
              "py":py_full(name),"init":py_init(name),
              "npy":py_full(c[1]),"ninit":py_init(c[1]),
              "hl":hl,
            }
            items.append(rec); got=True
    if got:
        pm=page.get_pixmap(dpi=DPI)
        images[str(pno+1)]="data:image/jpeg;base64,"+base64.b64encode(pm.tobytes("jpg")).decode()
        imgdim[str(pno+1)]=[pm.width, pm.height]
seen=set(); uniq=[]
for it in items:
    k=(it["national_code"], it["local_code"], it["name"])
    if k in seen: continue
    seen.add(k); uniq.append(it)
out={"version_label":"2024版",
     "source_file":"2024年6月版《成都市医疗服务项目价格汇编（2024版）》.pdf",
     "price_levels":["三甲","三乙","二甲","二乙","二乙以下"],
     "items":uniq,"page_images":images,"page_dims":imgdim}
os.makedirs(os.path.join(ROOT,'data'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT,'data','proto_data.json'),'w'), ensure_ascii=False)
print("items:", len(uniq), "pages_with_img:", len(images))
print("sample hl count:", len(uniq[0]["hl"]), "dims:", imgdim[str(uniq[0]["page_no"])])
print("sample hl:", uniq[0]["hl"][:3])
print("img total bytes ~", sum(len(v) for v in images.values()))
