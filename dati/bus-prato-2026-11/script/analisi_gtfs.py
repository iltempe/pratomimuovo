"""Rigenera i dataset sui bus urbani di Prato dal GTFS ufficiale della Regione Toscana.

Uso:
    1. Scarica il GTFS regionale: https://regionetoscana.smartregion.toscana.it/mobility/artifacts/gtfs
       (pagina del dataset: https://dati.toscana.it/dataset/rt-oraritb) e scompattalo in una cartella.
    2. python3 analisi_gtfs.py CARTELLA_GTFS [CARTELLA_OUTPUT]

Produce:
    - bus_in_viaggio_ogni_5_minuti.csv : corse urbane in viaggio ogni 5 minuti, per giorno tipo
    - linee_urbane_prato.csv           : corse, prima/ultima partenza, km stimati per linea
e stampa a video i numeri principali (ultima partenza, bus in viaggio, velocita' media).

Solo libreria standard di Python. Le linee urbane di Prato hanno agency_id 'UPO'.
"""
import csv
import datetime
import os
import sys
from collections import defaultdict

GTFS = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

# Giorni analizzati (feed AT del 17/11/2026). Cambiali se usi un feed piu' recente.
GIORNI = [
    ("20261118", "Feriale (mer 18/11)"),
    ("20261121", "Sabato (21/11)"),
    ("20261122", "Domenica (22/11)"),
    ("20261204", "Pilota notturno (ven 4/12)"),
]
PESI_ANNO = {"20261118": 250, "20261121": 52, "20261122": 63}  # giorni/anno per la stima dei km
PASSEGGERI_2024 = {  # Comune e AT, via La Nazione 19/06/2025
    "1+": 2623000, "2+": 1656000, "3+": 1300000, "11": 364000, "10": 110000, "5": 31616,
}
ORDINE = ["1+", "2+", "3+", "4", "9", "10", "11", "12", "5", "SC"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def rows(name):
    with open(os.path.join(GTFS, name), encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


routes = {r["route_id"]: r for r in rows("routes.txt") if r["agency_id"] == "UPO"}
cal = {r["service_id"]: r for r in rows("calendar.txt")}
exc = defaultdict(dict)
for r in rows("calendar_dates.txt"):
    exc[r["date"]][r["service_id"]] = r["exception_type"]


def servizi_attivi(ds):
    d = datetime.date(int(ds[:4]), int(ds[4:6]), int(ds[6:]))
    wd = DAYS[d.weekday()]
    s = {k for k, c in cal.items() if c[wd] == "1" and c["start_date"] <= ds <= c["end_date"]}
    for k, e in exc[ds].items():
        if e == "1":
            s.add(k)
        elif e == "2":
            s.discard(k)
    return s


trips = {r["trip_id"]: r for r in rows("trips.txt") if r["route_id"] in routes}


def minuti(t):
    h, m, s = t.split(":")
    return int(h) * 60 + int(m) + int(s) / 60


first, last, dist = {}, {}, defaultdict(float)
for r in rows("stop_times.txt"):
    t = r["trip_id"]
    if t not in trips:
        continue
    m = minuti(r["departure_time"] or r["arrival_time"])
    first[t] = min(first.get(t, 1e9), m)
    last[t] = max(last.get(t, -1), m)
    if r.get("shape_dist_traveled"):
        dist[t] = max(dist[t], float(r["shape_dist_traveled"]))  # metri


def fmt(m):
    return f"{int(m // 60):02d}.{int(round(m % 60)):02d}"


def corse(ds):
    a = servizi_attivi(ds)
    return [t for t, r in trips.items() if r["service_id"] in a]


# 1) bus in viaggio ogni 5 minuti
griglia = list(range(4 * 60, 26 * 60 + 1, 5))
serie = {}
for ds, lab in GIORNI:
    U = corse(ds)
    serie[lab] = [sum(1 for t in U if first[t] <= m <= last[t]) for m in griglia]
    km = sum(dist[t] for t in U) / 1000
    ore = sum(last[t] - first[t] for t in U) / 60
    print(f"{lab}: {len(U)} corse urbane, ultima partenza {fmt(max(first[t] for t in U))}, "
          f"prima {fmt(min(first[t] for t in U))}, velocita' media {km / ore:.1f} km/h")
with open(os.path.join(OUT, "bus_in_viaggio_ogni_5_minuti.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ora"] + [lab for _, lab in GIORNI])
    for i, m in enumerate(griglia):
        w.writerow([f"{(m // 60) % 24:02d}:{m % 60:02d}"] + [serie[lab][i] for _, lab in GIORNI])

# 2) tabella delle linee
info, km_anno = defaultdict(dict), defaultdict(float)
for ds, peso in PESI_ANNO.items():
    for t in corse(ds):
        ln = routes[trips[t]["route_id"]]["route_short_name"]
        km_anno[ln] += dist[t] / 1000 * peso
        d = info[ln].setdefault(ds, [0, 1e9, 0])
        d[0] += 1
        d[1] = min(d[1], first[t])
        d[2] = max(d[2], first[t])
nomi = {r["route_short_name"]: r["route_long_name"] for r in routes.values()}
with open(os.path.join(OUT, "linee_urbane_prato.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["linea", "percorso", "corse feriali", "prima partenza feriale", "ultima partenza feriale",
                "corse domenica", "km anno (stima da orari)", "passeggeri 2024 (Comune/AT)", "passeggeri per km"])
    for ln in ORDINE:
        fe = info[ln]["20261118"]
        do = info[ln].get("20261122", [0, 0, 0])
        p = PASSEGGERI_2024.get(ln, "")
        w.writerow([ln, nomi[ln], fe[0], fmt(fe[1]), fmt(fe[2]), do[0], round(km_anno[ln]), p,
                    f"{p / km_anno[ln]:.2f}" if p else ""])
print("CSV scritti in", os.path.abspath(OUT))
