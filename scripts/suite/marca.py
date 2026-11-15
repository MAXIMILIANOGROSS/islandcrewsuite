"""Island Crew Suite · marca común (cabra social) e IA gratuita del cliente."""
import os, re, json, base64, urllib.request
import core
AQUI = os.path.dirname(os.path.abspath(__file__))


def datauri(n="marca.jpg"):
    try: return "data:image/%s;base64," % ("png" if n.endswith(".png") else "jpeg") + base64.b64encode(open(os.path.join(AQUI, n), "rb").read()).decode()
    except Exception: return ""


def ia_json(prompt):
    """Gemini gratis y, si falla, Groq gratis. Devuelve JSON ya interpretado."""
    k = core.clave("GEMINI_API_KEY"); err = []
    if k:
        cuerpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}}).encode()
        for m in ("gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"):
            try:
                rq = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % m, cuerpo, {"Content-Type": "application/json", "x-goog-api-key": k})
                t = json.load(urllib.request.urlopen(rq, timeout=40))["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```(?:json)?|```$", "", t.strip()).strip())
            except Exception as e: err.append(m + ":" + str(e)[:40])
    g = core.clave("GROQ_API_KEY")
    if g:
        try:
            rq = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + g, "User-Agent": "IslandCrewSuite/1.0"})
            return json.loads(json.load(urllib.request.urlopen(rq, timeout=40))["choices"][0]["message"]["content"])
        except Exception as e: err.append("groq:" + str(e)[:40])
    raise RuntimeError("Sin IA ahora (" + (", ".join(err) or "falta la clave gratuita de Gemini; ponla repitiendo el asistente") + ").")


# ---------------- idiomas (ES · EN · IT · DE) ----------------
import threading
_L = {"x": None}
NOMBRES_IDIOMA = {"es": "español de España (tuteando)", "en": "English", "it": "italiano", "de": "Deutsch"}


def idioma_def():
    try: return json.load(open(os.path.join(core.carpeta_config(), "config.json"), encoding="utf8")).get("idioma", "es")
    except Exception: return "es"


def fijar(headers):
    """Recuerda el idioma elegido en la pantalla (cookie icl) para escribir los textos de la IA en ese idioma."""
    try:
        m = re.search(r"(?:^|;\s*)icl=([a-z]{2})", headers.get("Cookie") or "")
        _L["x"] = m.group(1) if m else None
    except Exception: _L["x"] = None


def codigo():
    return _L["x"] or idioma_def()


def lengua():
    return NOMBRES_IDIOMA.get(_L["x"] or idioma_def(), NOMBRES_IDIOMA["es"])


def _diccionario():
    import i18n_data
    d = {t[0]: list(t[1:]) for t in i18n_data.T}
    return d, [[p[0], list(p[1:])] for p in i18n_data.P]


_JS = r"""<script>(function(){var D=__D__,P=__P__,LG=["es","en","it","de"],NM={es:"Español",en:"English",it:"Italiano",de:"Deutsch"};
function ck(){var m=document.cookie.match(/(?:^|; )icl=([a-z]{2})/);return m?m[1]:"__DEF__"}
var L=ck();if(LG.indexOf(L)<0)L="es";var X=LG.indexOf(L)-1;
function t(s){if(X<0||!s)return s;var k=s.trim();if(!k)return s;var v=D[k];if(v)return v[X]?s.replace(k,v[X]):s;
for(var i=0;i<P.length;i++){var m=k.match(new RegExp(P[i][0]));if(m){var r=P[i][1][X];if(r)return s.replace(k,r.replace(/\$(\d)/g,function(_,n){return m[n]||""}))}}return s}
function w(n){if(n.nodeType==3){var x=t(n.nodeValue);if(x!==n.nodeValue)n.nodeValue=x;return}if(n.nodeType!=1)return;var g=n.tagName;if(g=="SCRIPT"||g=="STYLE"||n.id=="ic-lang")return;
["placeholder","title","aria-label"].forEach(function(a){var v=n.getAttribute(a);if(v){var x=t(v);if(x!==v)n.setAttribute(a,x)}});for(var c=n.firstChild;c;c=c.nextSibling)w(c)}
function selector(){var s=document.createElement("select");s.id="ic-lang";s.title="Idioma / Language";LG.forEach(function(l){var o=document.createElement("option");o.value=l;o.textContent="🌐 "+NM[l];if(l==L)o.selected=true;s.appendChild(o)});
s.style.cssText="background:#0008;color:#fff;border:1px solid #fff4;border-radius:8px;padding:5px 8px;font:13px system-ui;cursor:pointer;margin-right:12px;width:auto;flex:none";
s.onchange=function(){document.cookie="icl="+s.value+";path=/;max-age=31536000;SameSite=Lax";location.reload()};
var em=document.querySelector(".ic em");if(em){em.parentNode.insertBefore(s,em);s.style.marginLeft="auto";em.style.marginLeft="0"}
else{var h=document.querySelector(".h");if(h){s.style.marginLeft="auto";s.style.alignSelf="flex-start";h.appendChild(s)}else{s.style.cssText+=";position:fixed;top:10px;right:14px;z-index:99";document.body.appendChild(s)}}}
function ini(){document.documentElement.lang=L;document.title=t(document.title);w(document.body);selector();
new MutationObserver(function(ms){ms.forEach(function(m){if(m.type=="characterData"){var x=t(m.target.nodeValue);if(x!==m.target.nodeValue)m.target.nodeValue=x}else m.addedNodes.forEach(w)})}).observe(document.body,{childList:true,subtree:true,characterData:true})}
if(document.readyState=="loading")document.addEventListener("DOMContentLoaded",ini);else ini()})();</script>"""


def html(h):
    h = h.replace("__CABRA__", datauri()).replace("__CABRA_GRANDE__", datauri("cabra-social.jpg")).replace("__CONTROL__", datauri("control.jpg"))
    for k in ("carta", "publicaciones", "anuncios", "musica"): h = h.replace("__IC_%s__" % k, datauri("ic-%s.png" % k))
    for k in ("carta", "publicaciones", "anuncios"): h = h.replace("__AV_%s__" % k, datauri("av-%s.jpg" % k))
    for k in re.findall(r"__A_([a-z-]+)__", h): h = h.replace("__A_%s__" % k, datauri("a-%s.jpg" % k))
    try:
        d, p = _diccionario()
        js = _JS.replace("__D__", json.dumps(d, ensure_ascii=False)).replace("__P__", json.dumps(p, ensure_ascii=False)).replace("__DEF__", idioma_def())
        return h.replace("</body>", js + "</body>") if "</body>" in h else h + js
    except Exception: return h
