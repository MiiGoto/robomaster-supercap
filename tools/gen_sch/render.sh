#!/bin/sh
# render.sh outdir : export all sheets to PNG
cd "$1" && rm -f pg*.png all.pdf && kicad-cli sch export pdf -o all.pdf control_board.kicad_sch >/dev/null 2>&1 && pdftoppm -r ${2:-130} -png all.pdf pg && ls pg*.png
