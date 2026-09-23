"""Estrae le tabelle punteggi CdS Master (maschili e femminili) dai PDF in tabelle/ e genera data/punteggi.js.

Uso: pip install pymupdf && python3 scripts/estrai_tabelle.py
"""
import glob
import json
import os
import re

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = re.compile(r"^(?P<gara>.+?) CdS Master (?P<sesso>Maschili|Femminili) Cat\. (?P<cat>M[MF]\d+)$")
PERF = re.compile(r"^(?:(\d+)h)?(?:(\d+):)?(\d+)[.,](\d+)$")

# Nome visualizzato, tipo (corsa: tempo minore = meglio; concorso: misura maggiore = meglio), ordine
GARE = {
    "100 metri": ("100 m", "corsa", 1),
    "200 metri": ("200 m", "corsa", 2),
    "400 metri": ("400 m", "corsa", 3),
    "800 metri": ("800 m", "corsa", 4),
    "1500 metri": ("1500 m", "corsa", 5),
    "3000 metri": ("3000 m", "corsa", 6),
    "5000 metri": ("5000 m", "corsa", 7),
    "200 Hs H76-18.30": ("200 m ostacoli (H76 - 18,30)", "corsa", 8),
    "Staffetta 4 X 100": ("Staffetta 4x100", "corsa", 9),
    "Staffetta 4 X 400": ("Staffetta 4x400", "corsa", 10),
    "Salto in alto": ("Salto in alto", "concorso", 11),
    "Salto in lungo": ("Salto in lungo", "concorso", 12),
    "Salto triplo": ("Salto triplo", "concorso", 13),
    "Peso Kg 2.000": ("Peso 2 kg", "concorso", 14),
    "Peso Kg 3.000": ("Peso 3 kg", "concorso", 15),
    "Peso Kg 4.000": ("Peso 4 kg", "concorso", 16),
    "Disco Gr 750": ("Disco 750 g", "concorso", 17),
    "Disco Kg 1,000": ("Disco 1 kg", "concorso", 18),
    "Disco Kg 1,500": ("Disco 1,5 kg", "concorso", 19),
    "Disco Kg 2,000": ("Disco 2 kg", "concorso", 20),
    "Martello Kg 2.000": ("Martello 2 kg", "concorso", 21),
    "Martello Kg 3.000": ("Martello 3 kg", "concorso", 22),
    "Martello Kg 4.000": ("Martello 4 kg", "concorso", 23),
    "Giavellotto Gr 400": ("Giavellotto 400 g", "concorso", 24),
    "Giavellotto Gr 500": ("Giavellotto 500 g", "concorso", 25),
    "Giavellotto Gr 600": ("Giavellotto 600 g", "concorso", 26),
}
SESSI = {"Maschili": "M", "Femminili": "F"}


def in_centesimi(testo):
    m = PERF.match(testo)
    ore, minuti, sec, cent = m.groups()
    cent = int(cent.ljust(2, "0")[:2])
    return ((int(ore or 0) * 60 + int(minuti or 0)) * 60 + int(sec)) * 100 + cent


def main():
    tabelle = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "tabelle", "*", "*.pdf"))):
        for pagina in pymupdf.open(path):
            righe = [r.strip() for r in pagina.get_text().split("\n") if r.strip()]
            h = HEADER.match(righe[0])
            if not h:
                raise ValueError(f"{path}: intestazione inattesa {righe[0]!r}")
            valori = [r for r in righe[1:] if not r.startswith("Pag.")]
            if len(valori) % 2:
                raise ValueError(f"{path}: numero di valori dispari")
            chiave = GARE[h["gara"]][0]
            sesso = SESSI[h["sesso"]]
            tab = tabelle.setdefault((sesso, chiave), {}).setdefault(h["cat"], {})
            for perf, punti in zip(valori[::2], valori[1::2]):
                v = in_centesimi(perf)
                if v in tab and tab[v] != int(punti):
                    raise ValueError(f"{path}: {perf} con punteggi diversi")
                tab[v] = int(punti)

    out = {"sessi": [{"codice": "M", "nome": "Maschile", "gare": []},
                     {"codice": "F", "nome": "Femminile", "gare": []}]}
    gare_ordinate = sorted(GARE.values(), key=lambda g: g[2])
    for sesso in out["sessi"]:
        for nome, tipo, _ in gare_ordinate:
            if (sesso["codice"], nome) not in tabelle:
                continue
            categorie = {}
            for cat, tab in sorted(tabelle[(sesso["codice"], nome)].items()):
                coppie = sorted(tab.items(), reverse=(tipo == "concorso"))
                # dalla prestazione migliore alla peggiore i punti non devono mai crescere
                punti = [p for _, p in coppie]
                if any(b > a for a, b in zip(punti, punti[1:])):
                    raise ValueError(f"{sesso['codice']} {nome} {cat}: punteggi non monotoni")
                categorie[cat] = [[v, p] for v, p in coppie]
            sesso["gare"].append({"nome": nome, "tipo": tipo, "categorie": categorie})

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "punteggi.js"), "w") as f:
        f.write("// File generato da scripts/estrai_tabelle.py - non modificare a mano.\n")
        f.write("// Prestazioni in centesimi (tempo per le corse, cm per i concorsi), dalla migliore alla peggiore.\n")
        f.write("window.PUNTEGGI = ")
        json.dump(out, f, separators=(",", ":"))
        f.write(";\n")
    for sesso in out["sessi"]:
        for g in sesso["gare"]:
            print(sesso["codice"], g["nome"], {c: len(t) for c, t in g["categorie"].items()})


if __name__ == "__main__":
    main()
