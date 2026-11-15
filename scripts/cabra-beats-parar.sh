#!/bin/bash
# Para la web local de Cabra Beats (el trabajador y la música siguen sus propios ciclos).
for p in $(lsof -ti :3000 2>/dev/null); do kill "$p" 2>/dev/null; done
osascript -e 'display notification "Web local parada." with title "Cabra Beats"' >/dev/null 2>&1
