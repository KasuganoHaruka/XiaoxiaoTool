import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl=open(f'{ROOT}/prototype/index.template.html',encoding='utf-8').read()
data=open(f'{ROOT}/data/proto_data.json',encoding='utf-8').read()
# escape closing script tags just in case (none expected in data)
data=data.replace('</script>','<\\/script>')
html=tpl.replace('__DATA__', data)
out=f'{ROOT}/prototype/index.html'
open(out,'w',encoding='utf-8').write(html)
print('written', out, 'size', round(len(html.encode('utf-8'))/1024,1),'KB')
