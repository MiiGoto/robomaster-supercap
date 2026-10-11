#!/bin/sh
# render.sh board.kicad_pcb out.png [layers]
L=${3:-F.Cu,F.SilkS,F.CrtYd,Edge.Cuts}
kicad-cli pcb export svg --page-size-mode 2 --exclude-drawing-sheet -l $L -o /tmp/_b.svg "$1" >/dev/null 2>&1
python3 -c "import cairosvg; cairosvg.svg2png(url='/tmp/_b.svg', write_to='$2', output_width=1600, background_color='white')"
