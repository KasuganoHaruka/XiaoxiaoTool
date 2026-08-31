from PIL import Image, ImageDraw
import os
BASE='/root/projects/pdftool/.claude/worktrees/xiaoxiao/android/res'
SRC='/home/sora/Documents/mmexport1788191194471.jpg'  # user-provided avatar

def square(img):
    w,h=img.size; s=min(w,h)
    return img.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s))

src=square(Image.open(SRC).convert('RGB'))

def make(size, path):
    im=src.resize((size,size), Image.LANCZOS).convert('RGBA')
    # rounded-corner mask so it looks like an app icon on any launcher
    mask=Image.new('L',(size,size),0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,size-1,size-1], radius=int(size*0.22), fill=255)
    out=Image.new('RGBA',(size,size),(0,0,0,0)); out.paste(im,(0,0),mask)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    print('wrote', path, size)

for dens,px in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
    make(px, f'{BASE}/mipmap-{dens}/ic_launcher.png')
make(192, f'{BASE}/drawable/ic_launcher.png')
