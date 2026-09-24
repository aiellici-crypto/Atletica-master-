# Punteggi CdS Master

Applicazione web che calcola il punteggio CdS Master maschili e femminili: si sceglie il sesso, la specialità e la categoria, si inserisce la prestazione e viene mostrato il punteggio.

## Uso

Aprire `index.html` in un browser. Non serve un server né una connessione a internet.
`punteggi-cds-master.html` è la stessa app in un unico file, comoda da inviare o copiare sul telefono.

Formati accettati per la prestazione:

- corse: `12.34` / `12,34`, `1:45.30`, `1h07:10.37` (anche solo con virgole o punti: `1,45,30`, `1.45.30`)
- concorsi: misura in metri, es. `1,65` / `45.30`

Su telefoni e tablet, toccando il campo prestazione compare un tastierino con cifre, `:`, `,` e `.` al posto della tastiera di sistema.

Se la prestazione non compare esattamente in tabella si usa la prima riga non migliore della prestazione
(tempo uguale o superiore per le corse, misura uguale o inferiore per i concorsi). Una prestazione oltre il limite
peggiore della tabella vale 0 punti; una migliore del massimo riceve il punteggio massimo.

## Dati

Le tabelle originali sono in `tabelle/maschili/` e `tabelle/femminili/` (aggiornamento 2014). `data/punteggi.js` è generato da:

```
pip install pymupdf
python3 scripts/estrai_tabelle.py
```

Dopo aver rigenerato i dati va ricostruito anche `punteggi-cds-master.html` (copia di `index.html` con `data/punteggi.js` incorporato).
