"""Estrae le tabelle punteggi CdS Master Maschili dai PDF in tabelle/ e genera data/punteggi.js.

Uso: pip install pymupdf && python3 scripts/estrai_tabelle.py
"""
import glob
import json
import os
import re

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = re.compile(r"^(?P<gara>.+?) CdS Master Maschili Cat\. (?P<cat>MM\d+)$")
PERF = re.compile(r"^(?:(\d+)h)?(?:(\d+):)?(\d+)[.,](\d+)$")

# Nome visualizzato, tipo (corsa: tempo minore = meglio; concorso: misura maggiore = meglio), ordine
GARE = {
    "100 metri": ("100 m", "corsa", 1),
    "200 metri": ("200 m", "corsa", 2),
    "400 metri": ("400 m", "corsa", 3),
    "800 metri": ("800 m", "corsa", 4),
    "1500 metri": ("1500 m", "corsa", 5),
    "5000 metri": ("5000 m", "corsa", 6),
    "200 Hs H76-18.30": ("200 m ostacoli (H76 - 18,30)", "corsa", 7),
    "Staffetta 4 X 100": ("Staffetta 4x100", "corsa", 8),
    "Staffetta 4 X 400": ("Staffetta 4x400", "corsa", 9),
    "Salto in alto": ("Salto in alto", "concorso", 10),
    "Disco Kg 1,000": ("Disco 1 kg", "concorso", 11),
    "Disco Kg 1,500": ("Disco 1,5 kg", "concorso", 12),
    "Disco Kg 2,000": ("Disco 2 kg", "concorso", 13),
    "Giavellotto Gr 400": ("Giavellotto 400 g", "concorso", 14),
    "Giavellotto Gr 500": ("Giavellotto 500 g", "concorso", 15),
    "Giavellotto Gr 600": ("Giavellotto 600 g", "concorso", 16),
}


def in_centesimi(testo):
    m = PERF.match(testo)
    ore, minuti, sec, cent = m.groups()
    cent = int(cent.ljust(2, "0")[:2])
    return ((int(ore or 0) * 60 + int(minuti or 0)) * 60 + int(sec)) * 100 + cent


def main():
    tabelle = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "tabelle", "*.pdf"))):
        for pagina in pymupdf.open(path):
            righe = [r.strip() for r in pagina.get_text().split("\n") if r.strip()]
            h = HEADER.match(righe[0])
            if not h:
                raise ValueError(f"{path}: intestazione inattesa {righe[0]!r}")
            valori = [r for r in righe[1:] if not r.startswith("Pag.")]
            if len(valori) % 2:
                raise ValueError(f"{path}: numero di valori dispari")
            chiave = GARE[h["gara"]][0]
            tab = tabelle.setdefault(chiave, {}).setdefault(h["cat"], {})
            for perf, punti in zip(valori[::2], valori[1::2]):
                v = in_centesimi(perf)
                if v in tab and tab[v] != int(punti):
                    raise ValueError(f"{path}: {perf} con punteggi diversi")
                tab[v] = int(punti)

    out = {"gare": []}
    for nome_pdf, (nome, tipo, ordine) in sorted(GARE.items(), key=lambda g: g[1][2]):
        if nome not in tabelle:
            continue
        categorie = {}
        for cat, tab in sorted(tabelle[nome].items()):
            coppie = sorted(tab.items(), reverse=(tipo == "concorso"))
            # dalla prestazione migliore alla peggiore i punti non devono mai crescere
            punti = [p for _, p in coppie]
            if any(b > a for a, b in zip(punti, punti[1:])):
                raise ValueError(f"{nome} {cat}: punteggi non monotoni")
            categorie[cat] = [[v, p] for v, p in coppie]
        out["gare"].append({"nome": nome, "tipo": tipo, "categorie": categorie})

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "punteggi.js"), "w") as f:
        f.write("// File generato da scripts/estrai_tabelle.py - non modificare a mano.\n")
        f.write("// Prestazioni in centesimi (tempo per le corse, cm per i concorsi), dalla migliore alla peggiore.\n")
        f.write("window.PUNTEGGI = ")
        json.dump(out, f, separators=(",", ":"))
        f.write(";\n")
    for g in out["gare"]:
        print(g["nome"], {c: len(t) for c, t in g["categorie"].items()})


if __name__ == "__main__":
    main()
