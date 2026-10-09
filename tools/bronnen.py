"""Bronvermelding per begrip: in welke e-learning en les staat het, of is het aanvullende stof?

Bronteksten (geëxtraheerd uit de openbare e-learnings, repo fabianb88/minor-ce-elearnings):
  tools/bron_duurzaamheid.txt    — Duurzaamheid, circulariteit en systeemdenken (lessen 1–9)
  tools/bron_business_ethics.txt — Business Ethics (modules 1–5)
De koppeling hieronder is handmatig gecontroleerd tegen die teksten.
Gebruik `python tools/bronnen.py` om per begrip het aantal treffers in de bronteksten te zien.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EL = {"D": "E-learning Duurzaamheid, circulariteit en systeemdenken", "B": "E-learning Business Ethics"}
EL_KORT = {"D": "E-learning Duurzaamheid", "B": "E-learning Business Ethics"}

# Lestitels (overgenomen uit de e-learnings; bronteksten staan alleen lokaal, niet in de repo)
TITELS = {'D': {1: 'Introductie: Systeemdenken en de Drie Dimensies van Duurzaamheid', 2: 'Aarde als Systeem & Planetaire Grenzen', 3: 'Van Lineair naar Circulair: Economische Modellen en Strategieën', 4: 'Klimaatverandering & Infrastructuur: Fysica, Systemen en Uitdagingen', 5: 'Meervoudige Waardecreatie & Dubbele Materialiteit in Bedrijven', 6: 'Biomimicry & Natuurlijke Principes in Ontwerp', 7: 'Wicked Problems & Systeemdenken: Complexiteit en Analyse', 8: 'Casuïstiek & Strategische Besluitvorming: Systeemdenken in de Praktijk', 9: 'Synthese, Toets & Reflectie: Jouw Rol in Duurzame Ontwikkeling'},
          'B': {1: 'Economie & Systemen (kort)', 2: 'Psychologie & Systemen', 3: 'Organisaties & Macht', 4: 'Technologie, Macht & Morele Interventie', 5: 'Greenwashing (kort)'}}

# Begrip -> lessen waarin het behandeld wordt (D = Duurzaamheid les n, B = Business Ethics module n)
IN_ELEARNING = {
 "systeemdenken": ["D1", "D7"], "rloop": ["D7"], "bloop": ["D7"], "hefboom": ["D7"], "cld": ["D7"],
 "systeemgrens": ["D1"], "emergentie": ["D7"], "wicked": ["D7"], "lockin": ["D7"], "padafh": ["D7"],
 "tbl": ["D1"], "sdg": ["D1"], "ecodiensten": ["D1"],
 "pg_overzicht": ["D2"], "pg_klimaat": ["D2", "D4"], "pg_oceaan": ["D2"], "pg_biosfeer": ["D2"], "pg_land": ["D2"],
 "pg_zoetwater": ["D2"], "pg_biogeo": ["D2"], "pg_nieuw": ["D2"], "pg_ozon": ["D2"], "pg_aerosol": ["D2"],
 "atmosfeer": ["D2"], "hydrosfeer": ["D2"], "lithosfeer": ["D2"], "biosfeer": ["D2"],
 "lineair": ["D3"], "circulair": ["D3"], "r_refuse": ["D3"], "r_reduce": ["D3"], "r_reuse": ["D3"], "r_repair": ["D3"],
 "r_refurbish": ["D3"], "r_recycle": ["D3"], "r_recover": ["D3"], "lca": ["D3"],
 "paas": ["D3"], "deelplatform": ["D3"], "levensduur": ["D3"],
 "broeikas": ["D4"], "koolstofbudget": ["D4"], "tipping": ["D4"], "netcongestie": ["D4", "D8"], "albedo": ["D4"],
 "iirc": ["D5"], "kap_overzicht": ["D5"], "kap_fin": ["D5"], "kap_prod": ["D5"], "kap_int": ["D5"], "kap_mens": ["D5"],
 "kap_soc": ["D5"], "kap_nat": ["D5"], "dubbelemat": ["D5"], "insideout": ["D5"], "outsidein": ["D5"], "csrd": ["D5"],
 "biomimicry": ["D6"], "lifesprinciples": ["D6"], "regeneratief": ["D6"],
 "moreleecon": ["B1"], "externaliteit": ["B1"], "tragedy": ["B1"], "neolib": ["B1"], "kudde": ["B1", "B2"],
 "b_herdef": ["B2"], "b_minim": ["B2"], "b_versch": ["B2"], "b_normal": ["B2"], "structure": ["B2"], "agency": ["B2"],
 "piketty": ["B3"], "financ": ["B3"], "aandeelhouder": ["B3"], "stakeholder": ["B3"],
 "winner": ["B4"], "ant": ["B4"], "moreleinterventie": ["B4"],
 "greenwashing": ["B5"], "g_tradeoff": ["B5"], "g_vaag": ["B5"], "g_irrelevant": ["B5"], "g_symbolisch": ["B5"],
 "rladder": ["D3"],   # pseudo-begrip voor handgeschreven vragen
}

# Aanvullende stof: niet (zo) in de e-learnings; wel de oorspronkelijke literatuur
LITERATUUR = {
 "reductionisme": "algemene systeemdenken-literatuur", "ijsberg": "ijsbergmodel uit de systeemdenken-literatuur (o.a. Senge, 1990)",
 "mentaal": "Senge (1990), The Fifth Discipline", "vertraging": "Meadows (2008), Thinking in Systems",
 "voorraad": "Meadows (2008), Thinking in Systems", "fixes": "Senge (1990), systeemarchetypen",
 "shifting": "Senge (1990), systeemarchetypen", "limits": "Senge (1990), systeemarchetypen",
 "tam": "Rittel & Webber (1973), Dilemmas in a General Theory of Planning", "rebound": "Sorrell (2007), The Rebound Effect",
 "jevons": "Jevons (1865), The Coal Question", "sterk": "Neumayer (2013), Weak versus Strong Sustainability",
 "zwak": "Neumayer (2013), Weak versus Strong Sustainability", "absont": "UNEP (2011), Decoupling Natural Resource Use",
 "relont": "UNEP (2011), Decoupling Natural Resource Use", "r_rethink": "R-ladder R0–R9 (Potting e.a., PBL 2017)",
 "r_remanufacture": "R-ladder R0–R9 (Potting e.a., PBL 2017)", "r_repurpose": "R-ladder R0–R9 (Potting e.a., PBL 2017)",
 "downcycling": "Braungart & McDonough (2002), Cradle to Cradle", "c2c": "Braungart & McDonough (2002), Cradle to Cradle",
 "biokring": "Braungart & McDonough (2002); Ellen MacArthur Foundation", "techkring": "Braungart & McDonough (2002); Ellen MacArthur Foundation",
 "functioneleeenheid": "ISO 14040/14044 (LCA-norm)", "symbiose": "Chertow (2000), Industrial Symbiosis",
 "compensatie": "klimaatbeleid (CO₂-compensatie)", "scope1": "GHG Protocol (WRI/WBCSD)", "scope2": "GHG Protocol (WRI/WBCSD)",
 "scope3": "GHG Protocol (WRI/WBCSD)", "esrs": "EFRAG (2023), European Sustainability Reporting Standards",
 "ecoeff": "WBCSD (1992), eco-efficiëntie", "ostrom": "Ostrom (1990), Governing the Commons",
 "b_dehum": "Bandura (1999), het oorspronkelijke model van morele ontkoppeling",
 "b_schuld": "Bandura (1999), het oorspronkelijke model van morele ontkoppeling",
 "attitude": "gedragspsychologie (attitude-gedragskloof)", "greenhushing": "South Pole (2022), Net Zero and Beyond",
 "ecgt": "Richtlijn (EU) 2024/825 (Empowering Consumers for the Green Transition)",
}

def lesnaam(code):
    s, n = code[0], int(code[1:])
    return f"{EL_KORT[s]} · {'les' if s == 'D' else 'module'} {n}: {TITELS[s][n]}"

def bron_begrip(id_):
    """(in_elearning: bool, tekst) voor één begrip."""
    if id_ in IN_ELEARNING:
        return True, " + ".join(lesnaam(c) for c in IN_ELEARNING[id_])
    return False, "Aanvullende stof, niet in de e-learnings · bron: " + LITERATUUR.get(id_, "algemene vakliteratuur")

def bron_meerdere(ids):
    """Voor vragen met meerdere begrippen (koppelen, handgeschreven)."""
    ids = list(dict.fromkeys(ids))
    codes = list(dict.fromkeys(c for i in ids for c in IN_ELEARNING.get(i, [])))
    extra = [i for i in ids if i not in IN_ELEARNING]
    if not ids:
        return False, "Aanvullende stof, niet in de e-learnings · bron: algemene vakliteratuur"
    delen = [lesnaam(c) for c in codes]
    if extra:
        delen.append("aanvullend: " + "; ".join(dict.fromkeys(LITERATUUR.get(i, "vakliteratuur") for i in extra)))
    return (not extra), " + ".join(delen)

# Zoekpatronen om begrippen te herkennen in handgeschreven vragen (in 'uitleg.concept' en de categorie)
HERKEN = {
 "rladder": r"r-ladder|r0|refuse|recycle", "systeemdenken": r"systeemdenken", "hefboom": r"hefboom|meadows",
 "ijsberg": r"ijsberg", "rloop": r"r-loop|versterkend|positieve feedback", "bloop": r"b-loop|balancerend",
 "cld": r"causal loop", "fixes": r"fixes that fail", "wicked": r"wicked", "lockin": r"lock-in", "padafh": r"padafhankelijk",
 "rebound": r"rebound", "jevons": r"jevons", "tipping": r"tipping|kantelpunt", "koolstofbudget": r"koolstofbudget",
 "broeikas": r"broeikaseffect", "netcongestie": r"netcongestie", "lca": r"\blca\b|levenscyclus", "pg_overzicht": r"planetaire grens|planetaire grenzen",
 "pg_biogeo": r"stikstof|biogeochemi", "sferen": r"4 sferen", "tbl": r"triple bottom line|tbl", "sdg": r"sdg",
 "dubbelemat": r"dubbele materialiteit", "csrd": r"csrd", "esrs": r"esrs", "iirc": r"iirc|zes kapitalen|6 kapitalen",
 "paas": r"product-as-a-service|paas", "deelplatform": r"deelplatform|deeleconomie", "levensduur": r"levensduur",
 "biomimicry": r"biomimicry", "lifesprinciples": r"life.s principles", "regeneratief": r"regeneratie",
 "ecoeff": r"eco-efficiëntie", "moreleecon": r"morele economie", "externaliteit": r"externaliteit", "tragedy": r"commons",
 "ostrom": r"ostrom", "neolib": r"neoliberal", "piketty": r"piketty", "financ": r"financialisering",
 "aandeelhouder": r"aandeelhouder|friedman|shareholder", "stakeholder": r"stakeholdermodel",
 "b_herdef": r"morele ontkoppeling|bandura", "kudde": r"kuddegedrag", "structure": r"structure", "winner": r"winner",
 "ant": r"latour|actor-network", "moreleinterventie": r"morele interventie", "greenwashing": r"greenwashing",
 "ecgt": r"eu-regels|eu-claims|2024/825", "compensatie": r"compensatie", "absont": r"absolute .*ontkoppeling", "sterk": r"sterke duurzaamheid",
 "scope3": r"scope 3", "systeemgrens": r"systeemgrens", "vertraging": r"vertraging",
}
IN_ELEARNING["sferen"] = ["D2"]

def herken(tekst):
    t = tekst.lower()
    return [i for i, p in HERKEN.items() if re.search(p, t)]

if __name__ == "__main__":
    import sys, runpy
    sys.stdout.reconfigure(encoding="utf-8")
    begrippen = []
    for f in sorted((ROOT / "kb").glob("k[1-6]*.py")): begrippen += runpy.run_path(str(f))["BEGRIPPEN"]
    onbekend = [b["id"] for b in begrippen if b["id"] not in IN_ELEARNING and b["id"] not in LITERATUUR]
    print("zonder bronvermelding:", onbekend or "geen")
    n = sum(b["id"] in IN_ELEARNING for b in begrippen)
    print(f"{n} van {len(begrippen)} begrippen staan in de e-learnings")
