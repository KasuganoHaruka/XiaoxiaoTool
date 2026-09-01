import os, shutil
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl=open(f'{ROOT}/prototype/index.template.html',encoding='utf-8').read()
data=open(f'{ROOT}/data/proto_data.json',encoding='utf-8').read()
pymap=open(f'{ROOT}/data/pymap.json',encoding='utf-8').read()
# escape closing script tags just in case (none expected in data)
data=data.replace('</script>','<\\/script>')
pymap=pymap.replace('</script>','<\\/script>')
html=tpl.replace('__DATA__', data).replace('__PYMAP__', pymap)
out=f'{ROOT}/prototype/index.html'
open(out,'w',encoding='utf-8').write(html)

# pdf.js 原文渲染所需的静态资源，拷入被 8090 服务的 prototype/ 目录
os.makedirs(f'{ROOT}/prototype/pdfjs', exist_ok=True)
for f in ('pdf.min.js','pdf.worker.min.js'):
    shutil.copyfile(f'{ROOT}/vendor/pdfjs/{f}', f'{ROOT}/prototype/pdfjs/{f}')
shutil.copyfile(f'{ROOT}/data/doc.pdf', f'{ROOT}/prototype/doc.pdf')
print('written', out, 'size', round(len(html.encode('utf-8'))/1024,1),'KB  + pdfjs/ + doc.pdf')
