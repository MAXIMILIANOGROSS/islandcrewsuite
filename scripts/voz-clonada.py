#!/usr/bin/env python3
"""VOZ CLONADA de Cabra Beats Personal. Se ejecuta con el Python de la herramienta RVC (su entorno propio en el disco T5 EVO).
Órdenes:  estado · modelos · entrenar --nombre X --audios CARPETA [--epocas 120] · cantar --voz X --entrada CANCION --salida SALIDA.mp3 [--tono 0]
SOLO para tu voz o la de personas que te hayan dado permiso. Todo funciona en tu Mac y gratis."""
import re
import os, sys, json, glob, shutil, subprocess, argparse, time, random, urllib.request

RVC = os.environ.get("RVC_DIR") or "/Volumes/T5 EVO/IslandCrewAI/herramientas/RVC-WebUI-MacOS"


# sin esto la conversión de voz se cierra sola en el chip Apple (conflicto de librerías de cálculo)
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

def limpiar_basura():
    """Los discos externos (T5 EVO) crean copias «._archivo.py» que rompen librerías como fairseq. Se borran antes de usar la voz."""
    n = 0
    for base, ds, fs in os.walk(RVC):
        for f in fs:
            if f.startswith("._"):
                try: os.remove(os.path.join(base, f)); n += 1
                except OSError: pass
    # Segunda defensa: fairseq importa todo .py que no empiece por «_»; hacemos que también ignore los que empiezan por «.»
    for base in glob.glob(os.path.join(RVC, ".venv", "lib", "python*", "site-packages", "fairseq")):
        for r, ds, fs in os.walk(base):
            if "__init__.py" in fs:
                f = os.path.join(r, "__init__.py")
                try:
                    t = open(f, encoding="utf8").read()
                    t2 = t.replace('not file.startswith("_")', 'not file.startswith(("_", "."))').replace('not file.startswith("_")'.replace('"', "'"), "not file.startswith(('_', '.'))")
                    if t2 != t: open(f, "w", encoding="utf8").write(t2)
                except Exception: pass
    # Tercera defensa: esta versión de RVC nombra los trozos con la ruta completa y falla; se corrige para que use un nombre limpio
    pp = os.path.join(RVC, "infer", "modules", "train", "preprocess.py")
    try:
        t = open(pp, encoding="utf8").read()
        if "self.norm_write(tmp_audio, path, idx1)" in t:
            t = t.replace("self.norm_write(tmp_audio, path, idx1)", "self.norm_write(tmp_audio, __import__('re').sub(r'[^A-Za-z0-9_-]', '_', os.path.splitext(os.path.basename(path))[0]), idx1)")
            open(pp, "w", encoding="utf8").write(t)
    except Exception: pass
    # Cuarta defensa: el medidor de tono (RMVPE) de esta versión de RVC viene roto (un modelo de juguete que no coincide con el archivo). Se restituye el real.
    rp = os.path.join(RVC, "rvc", "f0", "rmvpe.py")
    try:
        t = open(rp, encoding="utf8").read()
        if "nn.Sequential(" in t and "class RMVPE(nn.Module):" in t:
            ini = t.index("class RMVPE(nn.Module):"); fin = t.index("    def compute_f0(", ini)
            nuevo = '''class RMVPE(F0Predictor):
    def __init__(self, model_path, device="cpu", is_half=True, use_jit=False):
        from .e2e import E2E
        super().__init__(160, 30, 8000, 16000, device)
        self.is_half = is_half
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.mel_extractor = MelSpectrogram(is_half, 128, 16000, 1024, 160, None, 30, 8000).to(device)
        model = E2E(4, 1, (2, 2))
        model.load_state_dict(torch.load(model_path, map_location="cpu", weights_only=False))
        model.eval()
        if is_half:
            model = model.half()
        self.model = model.to(device)
        cents_mapping = 20 * np.arange(360) + 1997.3794084376191
        self.cents_mapping = np.pad(cents_mapping, (4, 4))

'''
            open(rp, "w", encoding="utf8").write(t[:ini] + nuevo + t[fin:])
    except Exception: pass
    return n
HF = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/"
MODELOS = {"assets/hubert/hubert_base.pt": "hubert_base.pt", "assets/rmvpe/rmvpe.pt": "rmvpe.pt", "assets/pretrained_v2/f0G40k.pth": "pretrained_v2/f0G40k.pth", "assets/pretrained_v2/f0D40k.pth": "pretrained_v2/f0D40k.pth"}
def asegurar_deps():
    """Instala solo lo que falte en la herramienta de voz (p. ej. onnxruntime para medir el tono)."""
    try:  # variables de la herramienta (rutas de modelos); algunos pasos no las cargan solos
        for ln in open(os.path.join(RVC, ".env"), encoding="utf8"):
            if "=" in ln and not ln.lstrip().startswith("#"):
                k, v = [x.strip() for x in ln.split("=", 1)]
                if k: os.environ.setdefault(k, v)
    except OSError: pass
    for mod, pip in (("onnxruntime", "onnxruntime"), ("pybase16384", "pybase16384")):
        try: __import__(mod)
        except ImportError:
            print("Instalando", pip, "…", flush=True); subprocess.run([sys.executable, "-m", "pip", "install", pip], check=False)


def p(*a): print(*a, flush=True)

def reparar_modelos():
    """Si un entrenamiento terminó pero no dejó el archivo final de la voz, lo crea desde el último punto guardado."""
    hecho = []
    for g in sorted(glob.glob(os.path.join(RVC, "logs", "*", "G_latest.pth"))):
        nombre = os.path.basename(os.path.dirname(g))
        if nombre.startswith(".") or os.path.isfile(os.path.join(RVC, "assets/weights", nombre + ".pth")): continue
        try:
            for k, v in (("rmvpe_root", "assets/rmvpe"), ("weight_root", "assets/weights"), ("index_root", "logs"), ("outside_index_root", "assets/indices")): os.environ.setdefault(k, v)
            os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"; antes = os.getcwd(); os.chdir(RVC); sys.path.insert(0, RVC)
            import torch; it = torch.load(g, map_location="cpu", weights_only=False).get("iteration", "?")
            from infer.lib.train.process_ckpt import extract_small_model
            r = extract_small_model(os.path.relpath(g, RVC), nombre, "Island Crew", "40k", 1, f"{it}epoch", "v2"); os.chdir(antes)
            if os.path.isfile(os.path.join(RVC, "assets/weights", nombre + ".pth")): hecho.append(nombre); p(f"Voz «{nombre}» recuperada ({it} pasos).")
            else: p("No pude crear la voz", nombre, str(r)[-200:])
        except Exception as e: p("No pude recuperar", nombre, e)
    return hecho


def estado():
    r = {"rvc": os.path.isdir(RVC), "modelos_base": {k: os.path.isfile(os.path.join(RVC, k)) for k in MODELOS}, "voces": [], "demucs": False}
    r["modelos_ok"] = all(r["modelos_base"].values())
    r["voces"] = sorted(n for n in (os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(RVC, "assets/weights/*.pth"))) if not n.startswith(".") and not re.search(r"_e\d+_s\d+$", n))
    try:
        import importlib.util; r["demucs"] = importlib.util.find_spec("demucs") is not None
    except Exception: pass
    print(json.dumps(r)); return r

def bajar(destino, nombre):
    os.makedirs(os.path.dirname(destino), exist_ok=True); tmp = destino + ".part"
    rq = urllib.request.urlopen(urllib.request.Request(HF + nombre, headers={"User-Agent": "CabraBeats/1.0"}), timeout=60); tam = int(rq.headers.get("Content-Length") or 0); hecho = 0; t0 = time.time()
    with open(tmp, "wb") as f:
        while True:
            b = rq.read(1 << 20)
            if not b: break
            f.write(b); hecho += len(b)
            if tam and (time.time() - t0) > 2: p(f"  {os.path.basename(destino)}: {int(hecho * 100 / tam)} %"); t0 = time.time()
    os.replace(tmp, destino)

def modelos():
    for rel, nombre in MODELOS.items():
        d = os.path.join(RVC, rel)
        if os.path.isfile(d) and os.path.getsize(d) > 1e6: p("Ya está:", rel); continue
        p("Descargando", rel, "…"); bajar(d, nombre)
    p("Modelos base listos.")

def correr(cmd, **kw):
    limpiar_basura(); os.environ["COPYFILE_DISABLE"] = "1"; os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    p("▶", " ".join(cmd)[:200]); r = subprocess.run(cmd, cwd=RVC, **kw)
    if r.returncode != 0: sys.exit(f"Falló un paso (código {r.returncode}). Mira el mensaje de arriba.")

def entrenar(nombre, audios, epocas, sr="40k"):
    asegurar_deps(); limpiar_basura(); os.environ["COPYFILE_DISABLE"] = "1"; os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    if not os.path.isdir(audios) or not [f for f in os.listdir(audios) if f.lower().endswith((".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aiff", ".aif"))]: sys.exit("No encuentro grabaciones en esa carpeta.")
    for rel in MODELOS:
        if not os.path.isfile(os.path.join(RVC, rel)): sys.exit("Faltan los modelos base. Pulsa «Descargar modelos de voz» primero.")
    py = sys.executable; srn = 40000; exp = nombre; logs = os.path.join(RVC, "logs", exp); os.makedirs(logs, exist_ok=True)
    env = {**os.environ, "PYTORCH_ENABLE_MPS_FALLBACK": "1"}; dev = "mps"
    p("PASO 1/5 · Preparando tus grabaciones"); correr([py, "infer/modules/train/preprocess.py", audios, str(srn), "2", logs, "False", "3.0"], env=env)
    p("PASO 2/5 · Midiendo el tono de tu voz"); open(os.path.join(logs, "extract_f0_feature.log"), "w").close()
    correr([py, "infer/modules/train/extract_f0_print.py", logs, "2", "rmvpe", dev, "False"], env=env)
    p("PASO 3/5 · Aprendiendo el timbre de tu voz"); correr([py, "infer/modules/train/extract_feature_print.py", dev, "1", "0", "0", logs, "v2", "False"], env=env)
    p("PASO 4/5 · Entrenando el modelo (es la parte larga)")
    gt = os.path.join(logs, "0_gt_wavs"); fe = os.path.join(logs, "3_feature768"); f0 = os.path.join(logs, "2a_f0"); f0n = os.path.join(logs, "2b-f0nsf")
    limpiar_basura(); nm = lambda d: {n.split(".")[0] for n in os.listdir(d) if not n.startswith(".")}
    names = nm(gt) & nm(fe) & nm(f0) & nm(f0n)
    if not names: sys.exit("No se pudo preparar ninguna grabación. Usa audios más largos y claros (WAV o MP3).")
    lines = [f"{gt}/{n}.wav|{fe}/{n}.npy|{f0}/{n}.wav.npy|{f0n}/{n}.wav.npy|0" for n in names]; random.shuffle(lines); open(os.path.join(logs, "filelist.txt"), "w").write("\n".join(lines))
    cfg = os.path.join(logs, "config.json")
    if not os.path.exists(cfg): shutil.copyfile(os.path.join(RVC, "configs/v1/40k.json"), cfg)
    # el entrenamiento con el chip Apple no admite media precisión
    c = json.load(open(cfg)); c.setdefault("train", {})["fp16_run"] = False; json.dump(c, open(cfg, "w"), indent=4)
    correr([py, "infer/modules/train/train.py", "-e", exp, "-sr", "40k", "-f0", "1", "-bs", "4", "-te", str(epocas), "-se", "10", "-pg", "assets/pretrained_v2/f0G40k.pth", "-pd", "assets/pretrained_v2/f0D40k.pth", "-l", "1", "-c", "0", "-sw", "1", "-v", "v2", "-a", "Island Crew"], env=env)
    p("PASO 5/5 · Creando el índice de tu voz")
    import numpy as np, faiss
    arr = np.concatenate([np.load(os.path.join(fe, n)) for n in sorted(os.listdir(fe)) if not n.startswith(".")], 0); rng = np.arange(arr.shape[0]); np.random.shuffle(rng); arr = arr[rng]
    nivf = max(1, min(int(16 * np.sqrt(arr.shape[0])), arr.shape[0] // 39)); idx = faiss.index_factory(768, f"IVF{nivf},Flat"); idx.train(arr)
    for i in range(0, arr.shape[0], 8192): idx.add(arr[i:i + 8192])
    os.makedirs(os.path.join(RVC, "assets/indices"), exist_ok=True); faiss.write_index(idx, os.path.join(RVC, "assets/indices", f"{exp}.index"))
    peso = os.path.join(RVC, "assets/weights", f"{exp}.pth")
    if not os.path.isfile(peso): reparar_modelos()
    p("LISTO. Tu voz «" + exp + "» está creada." if os.path.isfile(peso) else "El entrenamiento terminó pero no encuentro el modelo final; revisa los pasos de arriba.")

def mejorar(nombre, audios, extra):
    """Sigue entrenando una voz ya creada con todas las grabaciones acumuladas. Antes guarda una copia para poder volver atrás."""
    logs = os.path.join(RVC, "logs", nombre); g = os.path.join(logs, "G_latest.pth"); d = os.path.join(logs, "D_latest.pth")
    if not (os.path.isfile(g) and os.path.isfile(d)): sys.exit("Esa voz no tiene punto de entrenamiento guardado. Créala primero con «Entrenar mi voz».")
    limpiar_basura(); os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    import torch; it = int(torch.load(g, map_location="cpu", weights_only=False).get("iteration") or 0)
    if it <= 0: sys.exit("No puedo leer cuántos pasos lleva esa voz.")
    resp = os.path.join(os.path.dirname(audios.rstrip("/")), "respaldo", time.strftime("%Y%m%d-%H%M%S") + f"-{it}pasos"); os.makedirs(resp, exist_ok=True)
    p("COPIA DE SEGURIDAD de tu voz actual en", resp)
    for src in (os.path.join(RVC, "assets/weights", nombre + ".pth"), os.path.join(RVC, "assets/indices", nombre + ".index"), g, d):
        if os.path.isfile(src): shutil.copy2(src, os.path.join(resp, os.path.basename(src)))
    for sub in ("0_gt_wavs", "1_16k_wavs", "2a_f0", "2b-f0nsf", "3_feature768"): shutil.rmtree(os.path.join(logs, sub), ignore_errors=True)
    p(f"Tu voz lleva {it} pasos de entrenamiento; le sumo {extra} más con todas tus grabaciones.")
    entrenar(nombre, audios, it + extra)


def cantar(voz, entrada, salida, tono=0):
    asegurar_deps(); limpiar_basura(); os.environ["COPYFILE_DISABLE"] = "1"; os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    if not os.path.isfile(os.path.join(RVC, "assets/weights", voz + ".pth")): sys.exit("Esa voz todavía no está entrenada.")
    if shutil.which("ffmpeg") is None: sys.exit("Falta ffmpeg.")
    import tempfile; tmp = tempfile.mkdtemp(prefix="vc-")
    p("PASO 1/3 · Separando la voz de la música"); correr([sys.executable, "-m", "demucs", "--two-stems=vocals", "-o", tmp, "-n", "htdemucs", entrada])
    base = os.path.splitext(os.path.basename(entrada))[0]; carp = glob.glob(os.path.join(tmp, "*", base))[0]
    voc, inst = os.path.join(carp, "vocals.wav"), os.path.join(carp, "no_vocals.wav")
    p("PASO 2/3 · Cambiando la voz por la tuya"); conv = os.path.join(tmp, "voz-convertida.wav")
    os.environ.update({"weight_root": "assets/weights", "index_root": "logs", "outside_index_root": "assets/indices", "rmvpe_root": "assets/rmvpe", "PYTORCH_ENABLE_MPS_FALLBACK": "1"})
    os.chdir(RVC); sys.path.insert(0, RVC); sys.argv = sys.argv[:1]
    from configs import Config; from infer.modules.vc import VC; from scipy.io import wavfile
    cfg = Config(); vc = VC(cfg); vc.get_vc(voz + ".pth")
    ind = os.path.join(RVC, "assets/indices", voz + ".index")
    _, wav = vc.vc_single(0, voc, int(tono), None, "rmvpe", ind if os.path.isfile(ind) else "", None, 0.66, 3, 0, 1, 0.33); wavfile.write(conv, wav[0], wav[1])
    p("PASO 3/3 · Mezclando con la música")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", inst, "-i", conv, "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0", "-codec:a", "libmp3lame", "-b:a", "192k", salida])
    shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode != 0: sys.exit("No pude mezclar el resultado.")
    p("LISTO:", salida)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("orden", choices=["estado", "modelos", "entrenar", "mejorar", "cantar", "limpiar"]); ap.add_argument("--nombre"); ap.add_argument("--audios"); ap.add_argument("--epocas", type=int, default=120)
    ap.add_argument("--voz"); ap.add_argument("--entrada"); ap.add_argument("--salida"); ap.add_argument("--tono", type=int, default=0); a = ap.parse_args()
    if a.orden == "estado": estado()
    elif a.orden == "modelos": modelos()
    elif a.orden == "entrenar": entrenar(re.sub(r"[^A-Za-z0-9_-]", "", a.nombre or "mivoz") if (re := re) else a.nombre, a.audios, a.epocas)
    elif a.orden == "mejorar": mejorar(re.sub(r"[^A-Za-z0-9_-]", "", a.nombre or "mivoz"), a.audios, a.epocas)
    elif a.orden == "limpiar": p("limpiados:", limpiar_basura()); reparar_modelos()
    else: cantar(a.voz, a.entrada, a.salida, a.tono)
