$dest = Join-Path $env:LOCALAPPDATA "IslandCrewSuite\programa"
Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like "$dest*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Remove-Item (Join-Path ([Environment]::GetFolderPath("Desktop")) "Island Crew Suite.lnk") -ErrorAction SilentlyContinue
foreach ($n in @("Carta Viva Island Crew","Publicaciones Island Crew","Anuncios Island Crew","Cabra Beats Island Crew")) { Remove-Item (Join-Path ([Environment]::GetFolderPath("Desktop")) "$n.lnk") -ErrorAction SilentlyContinue }
Remove-Item (Join-Path ([Environment]::GetFolderPath("Programs")) "Island Crew Suite") -Recurse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Island Crew Suite desinstalada. Tus cartas y datos NO se han borrado."
Start-Sleep -Seconds 3
