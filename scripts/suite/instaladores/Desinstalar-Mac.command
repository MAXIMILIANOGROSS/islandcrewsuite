#!/bin/bash
pkill -f "IslandCrewSuite/programa" 2>/dev/null || true
rm -rf "$HOME/Library/Application Support/IslandCrewSuite/programa"; for n in "Island Crew Suite" "Carta Viva Island Crew" "Publicaciones Island Crew" "Anuncios Island Crew" "Cabra Beats Island Crew"; do rm -rf "$HOME/Applications/$n.app" "$HOME/Desktop/$n"; done
echo "Island Crew Suite desinstalada. Tus cartas y datos NO se han borrado."
