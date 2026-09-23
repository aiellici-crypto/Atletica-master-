# Punteggi CdS Master

Applicazione web che calcola il punteggio CdS Master Maschili: si sceglie la specialità e la categoria, si inserisce la prestazione e viene mostrato il punteggio.

## Uso

Aprire `index.html` in un browser. Non serve un server né una connessione a internet.

Formati accettati per la prestazione:

- corse: `12,34` / `12.34`, `1:45,30`, `1h07:10,37`; sulla tastiera numerica del telefono si può usare solo la virgola: `1,45,30`, `1,07,10,37`
- concorsi: misura in metri, es. `1,65` / `45.30`

Se la prestazione non compare esattamente in tabella si usa la prima riga non migliore della prestazione
(tempo uguale o superiore per le corse, misura uguale o inferiore per i concorsi). Una prestazione oltre il limite
peggiore della tabella vale 0 punti; una migliore del massimo riceve il punteggio massimo.

## Dati

Le tabelle originali sono in `tabelle/`. `data/punteggi.js` è generato da:

```
pip install pymupdf
python3 scripts/estrai_tabelle.py
```
