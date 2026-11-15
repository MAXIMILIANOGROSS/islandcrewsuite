import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import centro
for p in ("hoy", "7d", "30d", "mes", "mes_ant", "trim", "anio"):
    d = centro.api(p, activos={"carta": True})
    assert d["global"] and d["unidades"]["musica"]["kpi"], p
    print(p, [(k["id"], k["v"]) for k in d["global"]][:5])
d = centro.api("custom", "2026-01-01", "2026-03-01"); print("custom ok", d["comparativa"]["carta"])
print(json.dumps(d["unidades"]["carta"]["kpi"], ensure_ascii=False))
print([a["t"] for a in d["alertas"]]); print(len(d["analista"]), "insights")
print(centro.informe("mensual"))
