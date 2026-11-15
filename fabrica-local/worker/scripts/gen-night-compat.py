#!/usr/bin/env python3
"""Genera la capa de compatibilidad noche (estilos en línea heredados) a partir de los hex usados en src/**/*.tsx.
Uso: python3 scripts/gen-night-compat.py  → reescribe el bloque entre los marcadores en src/styles/night.css"""
import re, glob, colorsys
N='body:not(:has(.nx-page)):not(:has(.hx))'
bg, fg = set(), set()
for f in glob.glob('src/**/*.tsx', recursive=True):
    t=open(f).read()
    for m in re.finditer(r'(background(?:Color)?|(?<![a-zA-Z-])color)\s*:\s*["\'`](#[0-9a-fA-F]{3,6})["\'`]', t):
        k,h=m.group(1),m.group(2).lower()
        if len(h)==4: h='#'+''.join(c*2 for c in h[1:])
        (bg if k.startswith('background') else fg).add(h)
bg={h for h in bg if len(h)==7}; fg={h for h in fg if len(h)==7}
def lum(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    return .2126*r+.7152*g+.0722*b
def hsv(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]; return colorsys.rgb_to_hsv(r,g,b)
def yellowish(h):
    hh,s,v=hsv(h); return 0.09<=hh<=0.19 and s>.25 and v>.7
light=sorted(h for h in bg if lum(h)>.72 and not yellowish(h) or (yellowish(h) and lum(h)>.85))
keep=sorted(h for h in bg if h not in light and (yellowish(h) or .35<lum(h)<=.72 and hsv(h)[1]>.35))
darktext=sorted(h for h in fg if lum(h)<.42 and not (hsv(h)[1]>.6 and hsv(h)[0]<.05 or hsv(h)[0]>.95))
red=sorted(h for h in fg if (hsv(h)[0]<.04 or hsv(h)[0]>.95) and hsv(h)[1]>.5 and lum(h)<.45)
amber=sorted(h for h in fg if .06<hsv(h)[0]<.14 and hsv(h)[1]>.6 and lum(h)<.5)
def ex(p):
    """Un estilo en línea escrito por el navegador (componentes de cliente) sale como 'background: rgb(r, g, b)'."""
    m=re.match(r'^(background(?:-color)?|color):(#[0-9a-f]{6})$',p)
    if not m: return [p]
    h=m.group(2); r,g,b=int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
    return [p, f'{m.group(1)}: rgb({r}, {g}, {b})']
def sel(props, extra=''):
    return ',\n'.join(f'{N} [style*="{q}" i]{extra}' for p in props for q in ex(p))
nk=''.join(f':not([style*="{q}" i])' for h in keep for q in ex(f'background:{h}'))
out='/* GEN-NIGHT-COMPAT:BEGIN (scripts/gen-night-compat.py) */\n'
out+=sel([f'background:{h}' for h in light]+[f'background-color:{h}' for h in light]+['background:white','background:#fff','background: rgb(255, 255, 255)','background: white','background:var(--paper)','background:var(--white)','background:var(--cyan)'])+'{background:rgba(255,255,255,.08)!important;color:#eaf2ff!important;border-color:rgba(255,255,255,.2)!important}\n'
out+=sel([f'color:{h}' for h in darktext]+['color:var(--ink)','color:var(--muted)','color:var(--ink-70)','color:#07182e'],nk)+'{color:#eaf2ff!important}\n'
if red: out+=sel([f'color:{h}' for h in red])+'{color:#ff9a9a!important}\n'
if amber: out+=sel([f'color:{h}' for h in amber])+'{color:#ffd27a!important}\n'
out+=sel(['solid #07182E','solid #0a1a3a','solid var(--ink)','solid #0b1a30'])+'{border-color:rgba(255,255,255,.22)!important}\n'
out+=sel(['0 #07182E','0 var(--ink)','0 #0a1a3a'])+'{box-shadow:0 10px 28px rgba(0,0,0,.35)!important}\n'
kp=[f'background:{h}' for h in keep]+['background:var(--yellow)','background:#ffd600']
kp=[q for p in kp for q in ex(p)]
out+=',\n'.join([f'{N} [style*="{p}" i]' for p in kp]+[f'{N} [style*="{p}" i] *' for p in kp])+'{color:#07182e!important}\n'
dark=sorted(h for h in bg if lum(h)<.35)
cls=['.ticker.tk-navy','.chapter-indicator','.signal-panel','.hero-photo','.hero-stamp','.profile-card-title','.employers','.drop-tag','.island-badge','.why','.merch-visual.tee-navy','.forsale','.worker-badge','.exec-section','.hub-cta-primary','.worker-filter-chip[data-active="true"]','.app-screen','.hx-strip','.sitebar']
ds=[f'{N} {c}' for c in cls]+[f'{N} [style*="{q}" i]' for h in dark for q in ex(f'background:{h}')]+[f'{N} [style*="background:var(--ink)" i]',f'{N} [style*="background:var(--ink-" i]',f'{N} [style*="background-color:var(--ink)" i]',f'{N} [style*="background:var(--ic-ink)" i]']
out+=',\n'.join(ds)+'{--ink:#07182e;--ink-70:rgba(7,24,46,.72);--paper:#fffdf7;--white:#fffdf7;--muted:#526071;--cyan:#e2f6fa;--ic-ink:#07182E;--ic-text:#07182E;--ic-text-muted:#526071;--ic-paper:#FFFDF7;--ic-cream:#F4E3B8;--ic-white:#ffffff}\n'
out+=',\n'.join(ds[len(cls):])+'{background-color:#07182e}\n' if False else ''
out+='/* GEN-NIGHT-COMPAT:END */\n'
p='src/styles/night.css'; s=open(p).read()
a=s.find('/* ── Capa de compatibilidad')
if a>=0:
    b=s.find('body:not(:has(.nx-page)):not(:has(.hx)) main :is(input,textarea', a); s=s[:a]+'@@GEN@@\n'+s[b:]
elif '/* GEN-NIGHT-COMPAT:BEGIN' in s:
    a=s.index('/* GEN-NIGHT-COMPAT:BEGIN'); b=s.index('/* GEN-NIGHT-COMPAT:END */\n')+len('/* GEN-NIGHT-COMPAT:END */\n'); s=s[:a]+'@@GEN@@\n'+s[b:]
s=s.replace('@@GEN@@\n',out)
open(p,'w').write(s)
print(len(light),'claros',len(keep),'amarillos/estado',len(darktext),'textos oscuros',red,amber)
