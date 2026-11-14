"""Rule-based rotation comparison + Climate Remix. Crop values are GENERIC approximate references, not local agronomy."""
from env import clamp
# water mm/season, N-fixation kg/ha (approx), soil-cover 0-1, drought sensitivity 0-1, family
CROPS = {"wheat": (450, 0, .6, .5, "cereal"), "barley": (400, 0, .55, .4, "cereal"), "maize": (600, 0, .45, .8, "cereal"), "oat": (380, 0, .55, .4, "cereal"), "sorghum": (380, 0, .5, .25, "cereal"),
         "sunflower": (500, 0, .4, .45, "oilseed"), "rapeseed": (450, 0, .6, .55, "oilseed"), "chickpea": (350, 50, .4, .35, "legume"), "lentil": (330, 45, .35, .35, "legume"),
         "pea": (380, 55, .4, .5, "legume"), "soybean": (520, 70, .45, .65, "legume"), "vetch": (300, 80, .8, .3, "legume"), "fallow": (0, 0, .1, 0, "fallow")}

def evaluate(seq, rain_mm, temp_c, rain_pct=0, temp_add=0, drought=0.0):
    supply = rain_mm * (1 + rain_pct / 100) * .6 * (1 - .4 * drought); rows = []
    for c in seq:
        w, n, cov, sens, fam = CROPS[c]; need = w * (1 + .04 * temp_add)
        stress = 0 if not need else clamp((need - supply) / need * (.6 + sens))
        rows.append({"crop": c, "water_mm": round(need), "stress": round(stress, 2), "n_fix": n, "cover": cov, "family": fam})
    k = len(rows); ms = sum(r["stress"] for r in rows) / k
    return {"seq": seq, "rows": rows, "water_mm": round(sum(r["water_mm"] for r in rows) / k), "stress": round(ms, 2), "cover": round(sum(r["cover"] for r in rows) / k, 2),
            "n_fix": round(sum(r["n_fix"] for r in rows) / k), "yield_risk": "low" if ms < .15 else "moderate" if ms < .35 else "high",
            "supply_mm": round(supply), "legumes": sum(r["family"] == "legume" for r in rows), "repeat_family": any(rows[i]["family"] == rows[i - 1]["family"] != "fallow" for i in range(k))}

def ai_sequence(rain_mm, temp_c, soil):
    ratio = rain_mm * .6 / 480
    seq = ["barley", "chickpea", "wheat", "vetch"] if ratio < .8 else ["wheat", "pea", "barley", "sunflower"] if ratio < 1.1 else ["maize", "soybean", "wheat", "rapeseed"]
    if soil and "clay" in soil.lower() and "chickpea" in seq: seq[seq.index("chickpea")] = "lentil"
    return seq

def compare(current, peer, rain_mm, temp_c, soil, soil_source, crops_known, rain_pct, temp_add, drought):
    cur = [c for c in current if c in CROPS] or ["wheat", "fallow"]
    strategies = [("current", "Current rotation", cur, "Built from the crop history you entered."),
                  ("peer", "Peer rotation", [c for c in (peer or []) if c in CROPS], "Used by a matched farm with similar NASA-derived climate. Their soil, practices and results may differ."),
                  ("ai", "AI recommendation", ai_sequence(rain_mm, temp_c, soil), "Rule-based: selected by water balance (effective rain vs crop need), legume–cereal–oilseed alternation and soil type. Not a trained yield model.")]
    out = []
    for key, name, seq, why in strategies:
        if not seq: out.append({"key": key, "name": name, "empty": True, "why": "No matched farm selected yet. Match in Discover to unlock."}); continue
        e = evaluate(seq, rain_mm, temp_c, rain_pct, temp_add, drought); e.update(key=key, name=name, why=why)
        e["pros"] = ([f"Nitrogen fixation ≈ {e['n_fix']} kg/ha/yr avg (generic estimate)"] if e["n_fix"] else []) + ([f"Higher soil cover ({e['cover']})"] if e["cover"] >= .55 else []) + (["Lower water demand"] if e["water_mm"] < 400 else [])
        e["cons"] = (["Same crop family in consecutive years (disease/pest build-up)"] if e["repeat_family"] else []) + (["High water-stress risk under this scenario"] if e["stress"] >= .35 else []) + (["No legume in rotation"] if not e["legumes"] else [])
        e["assumptions"] = ["Effective rain = 60% of annual NASA POWER rainfall (rough assumption)", "No irrigation", "Crop water/N values are generic references—verify locally", "Risk index is relative, NOT a yield prediction"]
        e["missing"] = ([] if soil_source == "farmer-tested" else ["No soil test results (pH, N, organic matter, drainage)"]) + ([] if crops_known else ["Crop history incomplete"]) + ["Prices, labour and machinery availability", "Local pest/disease pressure"]
        out.append(e)
    return out
