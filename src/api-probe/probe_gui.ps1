Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$exe = "C:\Users\Administrator\Documents\deepseek-harness\default-workspace\dist\EgoOpsSync.exe"
Get-Process -Name "EgoOpsSync" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep 1

Start-Process -FilePath $exe -WorkingDirectory "C:\Users\Administrator\Documents\deepseek-harness\default-workspace\dist" | Out-Null
Start-Sleep -Seconds 10

$procs = Get-Process -Name "EgoOpsSync" -ErrorAction SilentlyContinue
"进程数: $($procs.Count)"
$procs | Select-Object Id, MainWindowTitle | Format-Table -AutoSize

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$out = "C:\Users\Administrator\Documents\deepseek-harness\default-workspace\dist\screen.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"截图: $out"
