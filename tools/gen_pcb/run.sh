#!/bin/sh
# run.sh tag : build -> prep -> freeroute -> finish
set -e
T=$1
python3 build_pcb.py board.net $T.kicad_pcb | tail -2
python3 route.py prep $T.kicad_pcb ${T}z.kicad_pcb $T.dsn
timeout 590 xvfb-run -a java -jar freerouting.jar -de $T.dsn -do $T.ses -mp ${2:-60} > fr_$T.log 2>&1 || true
python3 route.py finish ${T}z.kicad_pcb $T.ses ${T}r.kicad_pcb | tail -1
grep -oE "^\[[a-z_]+\]" ${T}r_drc.rpt | sort | uniq -c
awk '/\[unconnected_items\]/{getline;getline;a=$0;getline;b=$0; print a" || "b}' ${T}r_drc.rpt | sed 's/ on F.Cu//g' | sort | uniq -c | sort -rn | head -25
