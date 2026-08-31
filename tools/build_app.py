import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl=open(f'{ROOT}/prototype/index.template.html',encoding='utf-8').read()
data=open(f'{ROOT}/data/proto_data.json',encoding='utf-8').read().replace('</script>','<\\/script>')
html=tpl.replace('__DATA__', data)

# 1) lock page zoom (in-app modal zoom is the only zoom)
html=html.replace(
 '<meta name="viewport" content="width=device-width, initial-scale=1"/>',
 '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover"/>')

# 2) app-mode: fill the screen, drop the phone frame / status bar / side legend
appmode='''<style id="appmode">
  html,body{height:100%}
  body{display:block;padding:0;margin:0;background:var(--bg);align-items:stretch;justify-content:flex-start}
  .phone{width:100vw;height:100vh;height:100dvh;border-radius:0;box-shadow:none}
  .statusbar{display:none}
  .legend{display:none}
</style>
</head>'''
html=html.replace('</head>', appmode, 1)

out=f'{ROOT}/android/assets/index.html'
open(out,'w',encoding='utf-8').write(html)
print('written', out, 'size', round(len(html.encode('utf-8'))/1024,1),'KB')
