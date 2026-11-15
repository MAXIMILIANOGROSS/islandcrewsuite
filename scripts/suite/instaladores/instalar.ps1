$ErrorActionPreference = "Stop"
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$raiz = Split-Path -Parent $aqui
$dest = Join-Path $env:LOCALAPPDATA "IslandCrewSuite\programa"
$paq = Join-Path $raiz "Paquetes\win.tar.xz"
if (Test-Path $paq) { $lista = @("Paquetes") } else { $lista = @("app", "runtime-win", "bin-win", "Licencias") }
foreach ($n in $lista) {
  if (-not (Test-Path (Join-Path $raiz $n))) { throw "Falta la carpeta $n en el pendrive. Copia el pendrive completo." }
}
Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like "$dest*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
New-Item -ItemType Directory -Path $dest -Force | Out-Null
if (Test-Path $paq) {
  & (Join-Path $env:WINDIR "System32\tar.exe") -xf $paq -C $dest
  if ($LASTEXITCODE -ne 0) { throw "No se pudo descomprimir el paquete. Necesitas Windows 10 (1803) o superior." }
} else {
Copy-Item (Join-Path $raiz "app") (Join-Path $dest "app") -Recurse
Copy-Item (Join-Path $raiz "runtime-win") (Join-Path $dest "runtime") -Recurse
Copy-Item (Join-Path $raiz "Licencias") (Join-Path $dest "Licencias") -Recurse
New-Item -ItemType Directory -Path (Join-Path $dest "app\bin") -Force | Out-Null
Copy-Item (Join-Path $raiz "bin-win\*") (Join-Path $dest "app\bin") -Recurse
}
Copy-Item (Join-Path $aqui "Desinstalar.ps1") $dest

$vbs = @'
Set s = CreateObject("WScript.Shell")
d = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
extra = ""
If WScript.Arguments.Count > 0 Then extra = " " & WScript.Arguments(0)
s.Run """" & d & "\runtime\python\pythonw.exe"" """ & d & "\app\scripts\suite\suite.py""" & extra, 0, False
'@
Set-Content -Path (Join-Path $dest "Iniciar.vbs") -Value $vbs -Encoding ASCII

$sh = New-Object -ComObject WScript.Shell
$menu = Join-Path ([Environment]::GetFolderPath("Programs")) "Island Crew Suite"
New-Item -ItemType Directory -Path $menu -Force | Out-Null
function Acceso($ruta, $args2, $nombre) {
  $l = $sh.CreateShortcut($ruta)
  $l.TargetPath = Join-Path $env:WINDIR "System32\wscript.exe"
  $l.Arguments = $args2
  $l.WorkingDirectory = $dest
  $l.Description = $nombre
  $l.IconLocation = (Join-Path $dest "app\icono.ico")
  $l.Save()
}
$ini = '"' + (Join-Path $dest "Iniciar.vbs") + '"'
function AccesoIcono($ruta, $args2, $nombre, $ico) {
  $l = $sh.CreateShortcut($ruta)
  $l.TargetPath = Join-Path $env:WINDIR "System32\wscript.exe"
  $l.Arguments = $args2
  $l.WorkingDirectory = $dest
  $l.Description = $nombre
  $l.IconLocation = (Join-Path $dest ("app\" + $ico))
  $l.Save()
}
foreach ($f in @(@("carta","Carta Viva Island Crew"), @("publicaciones","Publicaciones Island Crew"), @("anuncios","Anuncios Island Crew"), @("musica","Cabra Beats Island Crew"))) {
  $a2 = $ini + " --abrir " + $f[0]
  AccesoIcono (Join-Path $menu ($f[1] + ".lnk")) $a2 $f[1] ($f[0] + ".ico")
}
Acceso (Join-Path ([Environment]::GetFolderPath("Desktop")) "Island Crew Suite.lnk") $ini "Island Crew Marketing Suite"
Acceso (Join-Path $menu "Island Crew Suite.lnk") $ini "Island Crew Marketing Suite"
Acceso (Join-Path $menu "Repetir asistente.lnk") ($ini + " --asistente") "Repetir el asistente de configuracion"
$u = $sh.CreateShortcut((Join-Path $menu "Desinstalar.lnk"))
$u.TargetPath = "powershell.exe"
$u.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"" + (Join-Path $dest "Desinstalar.ps1") + "`""
$u.Save()

Write-Host ""
Write-Host " Instalado. Abriendo Island Crew Suite..."
Start-Process (Join-Path $env:WINDIR "System32\wscript.exe") -ArgumentList $ini
