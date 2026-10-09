"""Genereert app/vragen.js uit de kennisbank (tools/kb) en de handgeschreven vragen (tools/hand.json).

Gebruik:  python tools/genereer.py
De uitvoer is deterministisch (vaste seed), zodat vraag-id's stabiel blijven en voortgang bewaard blijft.
"""
import json, random, re, runpy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KB = ROOT / "kb"
UIT = ROOT.parent / "app" / "vragen.js"

CATEGORIEEN = [
    "Systeemdenken", "Complexiteit", "Duurzaamheid", "Ecologische grenzen", "Circulariteit",
    "Businessmodellen", "Klimaat & energie", "Rapportage & waarde", "Ontwerp", "Ethiek & economie",
    "Gedrag & verantwoordelijkheid", "Technologie & samenleving", "Greenwashing & claims", "Integrale casussen",
]

# ---------- laden ----------
begrippen, volgorde = [], []
for f in sorted(KB.glob("k*.py")):
    ns = runpy.run_path(str(f))
    begrippen += ns.get("BEGRIPPEN", [])
    volgorde += ns.get("VOLGORDE", [])
B = {b["id"]: b for b in begrippen}
hand = json.loads((ROOT / "hand.json").read_text(encoding="utf-8"))
BR = runpy.run_path(str(ROOT / "bronnen.py"))
bron_begrip, bron_meerdere, herken = BR["bron_begrip"], BR["bron_meerdere"], BR["herken"]
IN_EL = BR["IN_ELEARNING"]
HANDMATIG = {  # vraag-id -> begrippen (gaat voor automatische herkenning)
 "v-3": ["lineair"], "v-8": ["shifting"], "v-9": ["limits"], "v-15": ["pg_biosfeer", "ecodiensten"], "v-17": ["dubbelemat", "csrd"],
 "h-3": ["rloop", "pg_klimaat"], "h-10": ["tragedy"], "h-12": ["hefboom"], "h-13": ["ijsberg", "mentaal"], "h-27": ["ijsberg"],
 "h-32": ["dubbelemat", "csrd"], "h-33": ["rloop", "albedo"], "h-35": ["cld", "hefboom"], "h-36": ["lockin", "externaliteit", "rebound", "tragedy"],
 "h-37": ["rloop", "bloop", "tipping", "padafh"], "h-42": ["aandeelhouder", "piketty", "ant", "winner"],
 "h-45": ["paas", "deelplatform", "levensduur", "r_refurbish"], "h-47": ["wicked", "kudde", "structure", "neolib"],
 "h-48": ["hefboom", "aandeelhouder", "financ", "paas"], "h-49": ["greenwashing", "g_symbolisch", "absont"],
 "h-50": ["rebound", "systeemgrens", "netcongestie"], "h-51": ["structure", "agency", "lockin", "wicked", "pg_biogeo"],
 "h-53": ["lca", "deelplatform", "financ"], "h-54": ["tragedy", "ostrom"], "h-55": ["neolib", "piketty", "tbl"],
 "h-56": ["fixes", "rloop", "vertraging"], "h-57": ["dubbelemat", "csrd"], "h-58": ["winner", "ant", "moreleinterventie"],
 "h-59": ["tbl", "pg_overzicht", "absont"], "h-5": ["b_versch"], "h-41": ["b_herdef", "b_minim", "b_versch", "b_normal"],
}
def bron(ids):
    el, t = bron_meerdere(ids) if len(ids) != 1 else bron_begrip(ids[0])
    return dict(el=el, t=t)

fouten, waarschuwingen = [], []
if len(B) != len(begrippen):
    fouten.append("dubbele begrip-id's")
for b in begrippen:
    if b["cat"] not in CATEGORIEEN: fouten.append(f"{b['id']}: onbekende categorie {b['cat']}")
    for v in b["verwar"]:
        if v not in B: fouten.append(f"{b['id']}: verwar-id '{v}' bestaat niet")
        if v == b["id"]: fouten.append(f"{b['id']}: verwijst naar zichzelf")
    if len(b["verwar"]) < 2: fouten.append(f"{b['id']}: te weinig afleiders")
    if len(b["casus"]) < 6: fouten.append(f"{b['id']}: {len(b['casus'])} casussen (minimaal 6)")
    if b["id"] not in IN_EL and b["id"] not in BR["LITERATUUR"]: fouten.append(f"{b['id']}: geen bronvermelding")

rng = random.Random(2026)
kaal = lambda naam: re.sub(r"\s*\([^)]*\)\s*$", "", naam)   # 'Hefboompunt (Meadows)' -> 'Hefboompunt'

def stam(b):
    i = b["id"]
    if i.startswith("r_"): return "Welke R-strategie is dit?"
    if i.startswith("pg_") and i != "pg_overzicht": return "Welke planetaire grens is hier het meest direct in het geding?"
    if i.startswith("kap_") and i != "kap_overzicht": return "Welk kapitaal uit het IIRC-raamwerk is dit?"
    if i.startswith("b_"): return "Welk mechanisme van morele ontkoppeling (Bandura) zie je hier?"
    if i.startswith("g_"): return "Welke vorm van greenwashing is dit?"
    if i.startswith("scope"): return "Onder welke scope valt deze uitstoot?"
    if i in ("atmosfeer", "hydrosfeer", "lithosfeer", "biosfeer"): return "Welke sfeer wordt hier het meest direct geraakt?"
    return rng.choice(["Welk begrip past hier het best bij?", "Welk concept beschrijft dit het best?",
                       "Wat wordt hier het best geïllustreerd?", "Welk begrip hoort bij deze situatie?"])

def kies_afleiders(b, n=3):
    """Bij e-learningbegrippen eerst afleiders die ook in de e-learning staan:
    1) eigen 'verwar' uit de e-learning, 2) e-learningbegrippen uit dezelfde groep (r_, pg_, kap_, b_, g_), 3) overige 'verwar'."""
    if b["id"] not in IN_EL:
        return rng.sample(b["verwar"], min(n, len(b["verwar"])))
    groep = b["id"].split("_")[0] + "_" if "_" in b["id"] else None
    t1 = [v for v in b["verwar"] if v in IN_EL]
    t2 = [i for i in B if groep and i.startswith(groep) and i != b["id"] and i in IN_EL and i not in t1] if groep else []
    t2b = [i for i in B if B[i]["cat"] == b["cat"] and i != b["id"] and i in IN_EL and i not in t1 and i not in t2]
    t3 = [v for v in b["verwar"] if v not in IN_EL]
    uit = []
    for tier in (t1, t2, t2b, t3):
        rng.shuffle(tier); uit += tier[: n - len(uit)]
    return uit

def afleiders_uitleg(ids):
    return " · ".join(f"{B[i]['naam']}: {B[i]['kort']}." for i in ids)

vragen = []
def voeg(q): vragen.append(q)

# ---------- 1. casus -> begrip ----------
for b in begrippen:
    for n, casus in enumerate(b["casus"]):
        afl = kies_afleiders(b)
        tekst = (f"Iemand zegt: {casus}" if casus.startswith("‘") else casus)
        voeg(dict(id=f"c-{b['id']}-{n}", t="mc", cat=b["cat"], niv=2, b=bron([b["id"]]), v=tekst, s=stam(b),
                  o=[b["naam"]] + [B[a]["naam"] for a in afl], c=0,
                  u=dict(goed=f"Dit is {b['naam']}: {b['df']}", concept=b["naam"],
                         afleider="Waarom niet de rest? " + afleiders_uitleg(afl))))

# ---------- 2. definitie -> begrip ----------
for b in begrippen:
    afl = kies_afleiders(b)
    naam = kaal(b["naam"])
    if naam.lower() in b["df"].lower():
        waarschuwingen.append(f"definitie van {b['id']} bevat de naam zelf — overgeslagen")
        continue
    opties = [naam] + [kaal(B[a]["naam"]) for a in afl]
    if len(set(opties)) < len(opties):
        fouten.append(f"{b['id']}: dubbele kale namen in definitievraag")
    voeg(dict(id=f"d-{b['id']}", t="mc", cat=b["cat"], niv=1, b=bron([b["id"]]), v=b["df"], s="Welk begrip hoort bij deze omschrijving?",
              o=opties, c=0,
              u=dict(goed=f"Dit is de omschrijving van {b['naam']}.", concept=b["naam"],
                     afleider="Waarom niet de rest? " + afleiders_uitleg(afl))))

# ---------- 3. begrip -> welke casus ----------
for b in begrippen:
    afl = kies_afleiders(b)
    goed = rng.choice(b["casus"])
    fout = [rng.choice(B[a]["casus"]) for a in afl]
    voeg(dict(id=f"x-{b['id']}", t="mc", cat=b["cat"], niv=2, b=bron([b["id"]]),
              v=f"Welke situatie is het beste voorbeeld van: {b['naam']}?", s="Kies de situatie die past.",
              o=[goed] + fout, c=0,
              u=dict(goed=f"{b['naam']}: {b['df']}", concept=b["naam"],
                     afleider="De andere situaties zijn voorbeelden van: " + afleiders_uitleg(afl))))

# ---------- 4. koppelen ----------
for b in begrippen:
    if len(b["verwar"]) < 3: continue
    groep = [b["id"]] + kies_afleiders(b)
    paren = [[B[g]["naam"], rng.choice(B[g]["casus"])] for g in groep]
    voeg(dict(id=f"k-{b['id']}", t="koppelen", cat=b["cat"], niv=2, b=bron(groep),
              v="Koppel elk begrip aan de situatie die erbij hoort.", paren=paren,
              u=dict(goed=" · ".join(f"{B[g]['naam']}: {B[g]['kort']}." for g in groep),
                     concept=", ".join(B[g]["naam"] for g in groep))))

# ---------- 5. volgorde (extra) ----------
for n, q in enumerate(volgorde):
    voeg(dict(id=f"v-{n}", t="volgorde", cat=q["categorie"], niv=2, v=q["vraag"], items=q["items"], u=q["uitleg"],
              b=bron(HANDMATIG.get(f"v-{n}") or herken(q["uitleg"]["concept"] + " " + q["vraag"]))))

# ---------- 6. handgeschreven vragen (klassikale versie) ----------
TREFWOORDEN = [
    ("Integrale casussen", []),  # ronde 5
    ("Rapportage & waarde", ["rapportage", "materialiteit", "kapitalen", "csrd"]),
    ("Circulariteit", ["r-ladder", "lca", "circulariteit"]),
    ("Businessmodellen", ["businessmodel"]),
    ("Klimaat & energie", ["klimaat", "energie"]),
    ("Ecologische grenzen", ["planetaire", "ecologische", "stikstof", "sferen"]),
    ("Systeemdenken", ["systeem", "meadows", "ijsberg", "feedback", "rebound"]),
    ("Complexiteit", ["complexiteit", "lock-in"]),
    ("Greenwashing & claims", ["greenwashing", "claims"]),
    ("Technologie & samenleving", ["technologie"]),
    ("Gedrag & verantwoordelijkheid", ["ontkoppeling", "gedrag"]),
    ("Ontwerp", ["ontwerp"]),
    ("Duurzaamheid", ["duurzaamheid"]),
    ("Ethiek & economie", ["organisatie", "business ethics", "commons", "denkers", "economie"]),
]
def hand_cat(q):
    if q["ronde"] == 5: return "Integrale casussen"
    c = q["categorie"].lower()
    for cat, woorden in TREFWOORDEN[1:]:
        if any(w in c for w in woorden): return cat
    waarschuwingen.append(f"geen categorie voor '{q['categorie']}'")
    return "Integrale casussen"

for n, q in enumerate(hand):
    basis = dict(id=f"h-{n}", cat=hand_cat(q), niv=3 if q["ronde"] == 5 else 2, v=q["vraag"], u=q["uitleg"],
                 b=bron(HANDMATIG.get(f"h-{n}") or herken(q["uitleg"]["concept"] + " " + q["categorie"])))
    if q["type"] == "mc":
        basis.update(t="mc", o=q["opties"], c=q["correct"], s="")
    elif q["type"] == "volgorde":
        basis.update(t="volgorde", items=q["items"])
    else:
        basis.update(t="koppelen", paren=q["paren"])
    voeg(basis)

# ---------- validatie ----------
ids, sleutels = set(), set()
for q in vragen:
    if q["id"] in ids: fouten.append(f"dubbel id {q['id']}")
    ids.add(q["id"])
    k = q["v"] + json.dumps(q.get("o") or q.get("items") or q.get("paren"), ensure_ascii=False)
    if k in sleutels: fouten.append(f"dubbele vraag {q['id']}")
    sleutels.add(k)
    if q["t"] == "mc":
        if len(set(q["o"])) != len(q["o"]): fouten.append(f"{q['id']}: dubbele opties")
        if not (0 <= q["c"] < len(q["o"])): fouten.append(f"{q['id']}: ongeldig correct")
    if q["t"] == "koppelen":
        if len({p[0] for p in q["paren"]}) != 4 or len({p[1] for p in q["paren"]}) != 4:
            fouten.append(f"{q['id']}: koppelen niet uniek")
    if q["cat"] not in CATEGORIEEN: fouten.append(f"{q['id']}: categorie {q['cat']}")
    if not q["u"].get("goed"): fouten.append(f"{q['id']}: geen uitleg")

alle_casussen = [c for b in begrippen for c in b["casus"]]
dubbel = {c for c in alle_casussen if alle_casussen.count(c) > 1}
for c in dubbel: waarschuwingen.append(f"casus komt vaker voor: {c[:60]}")

for w in waarschuwingen: print("WAARSCHUWING:", w)
if fouten:
    for f in fouten: print("FOUT:", f)
    sys.exit(1)

per_type = {}
for q in vragen: per_type[q["t"]] = per_type.get(q["t"], 0) + 1
per_cat = {c: sum(1 for q in vragen if q["cat"] == c) for c in CATEGORIEEN}
data = dict(versie=len(vragen), categorieen=CATEGORIEEN,
            begrippen={b["id"]: dict(naam=b["naam"], cat=b["cat"], kort=b["kort"], df=b["df"]) for b in begrippen},
            vragen=vragen)
UIT.write_text("/* Gegenereerd door tools/genereer.py — niet handmatig bewerken */\nwindow.CE_DATA = "
               + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"{len(begrippen)} begrippen, {len(vragen)} vragen -> {UIT.name} ({UIT.stat().st_size // 1024} KB)")
print("per type:", per_type)
print("per categorie:", per_cat)
