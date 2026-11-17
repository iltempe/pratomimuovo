# I dati degli autobus a Prato (novembre 2026)

Dataset dell'articolo **"I dati degli autobus a Prato"** di PratoMiMuovo / @iltempe.
Descrivono la rete urbana di Prato come risulta dagli orari ufficiali di Autolinee Toscane, pubblicati come dati aperti dalla Regione Toscana.

## File

| File | Contenuto |
| --- | --- |
| `bus_in_viaggio_ogni_5_minuti.csv` | Numero di corse urbane in viaggio ogni 5 minuti, dalle 04:00 alle 02:00, in quattro giorni tipo: feriale (mer 18/11/2026), sabato (21/11), domenica (22/11) e prima sera della sperimentazione notturna (ven 4/12). |
| `linee_urbane_prato.csv` | Per ogni linea urbana: percorso, corse feriali, prima e ultima partenza feriale, corse la domenica, km l'anno stimati, passeggeri 2024 e passeggeri per km. |
| `grafici/` | Grafico dei bus in viaggio, mappe della rete la sera, tabella delle linee. |
| `script/analisi_gtfs.py` | Script che rigenera i due CSV dal GTFS ufficiale. Solo libreria standard di Python. |

## Numeri principali

- Ultima partenza urbana: **21.33** (linea 3+, dalla stazione), tutti i giorni. Prima partenza: 5.15 (5.35 la domenica).
- Corse urbane: **1.036** nel feriale, 998 il sabato, **383** la domenica.
- Bus urbani in viaggio nel feriale: 40–60 di giorno, 11 alle 21, 1 alle 22, 0 dalle 22.03.
- Velocità media dei bus urbani: 18,3 km/h nel feriale, fermate comprese.
- Ultimo treno da Firenze SMN: parte alle 00.25 e arriva a Prato Centrale alle 00.52, ogni giorno.

## Fonti

- Orari: [GTFS della Regione Toscana](https://dati.toscana.it/dataset/rt-oraritb), feed Autolinee Toscane del 17/11/2026 (agency `UPO` = urbano di Prato) e feed Trenitalia.
- Passeggeri 2024 per linea: dati di Comune e Autolinee Toscane riportati da [La Nazione, 19/06/2025](https://www.lanazione.it/prato/cronaca/lautobus-piace-di-piu-oltre-ab101d3a). Per le linee 4, 9, 12 e SC non sono pubblici.
- Confine comunale nelle mappe: [OpenStreetMap](https://www.openstreetmap.org/relation/280245), © OpenStreetMap contributors.

## Metodo

- **Corse in viaggio**: una corsa conta in un dato minuto se, secondo l'orario, è tra la prima e l'ultima fermata. Ogni corsa in viaggio corrisponde a un bus in strada.
- **Velocità media**: km di tutte le corse urbane del giorno (`shape_dist_traveled`) divisi per le loro ore di marcia.
- **Km l'anno (stima)**: km del feriale × 250 + km del sabato × 52 + km della domenica × 63. Il totale stimato (3,6 milioni) è il 7% sopra il dato ufficiale di 3.368.000 km, perché applica l'orario di novembre a tutto l'anno.
- I numeri sono stati calcolati con due programmi indipendenti e coincidono; questo script rigenera i CSV identici.

## Limiti

- Gli orari sono il servizio **programmato**: corse saltate e ritardi non si vedono.
- I passeggeri sono pubblici solo come totale annuo per linea: non c'è il dato per fascia oraria.
- Nel feed del 17/11/2026 le corse notturne della sperimentazione compaiono il 4 e il 5 dicembre; lunedì 7 dicembre non c'è.

## Rifare i conti

```
# scarica e scompatta il GTFS regionale
curl -L -o gtfs.zip https://regionetoscana.smartregion.toscana.it/mobility/artifacts/gtfs
unzip gtfs.zip -d gtfs
python3 script/analisi_gtfs.py gtfs .
```

Con un feed più recente cambia le date in `GIORNI` all'inizio dello script.
