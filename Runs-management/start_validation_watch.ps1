$thresholdDirectory = $PSScriptRoot
$thresholdPidFile = Join-Path $thresholdDirectory 'threshold_watch.pid'
if (Test-Path -LiteralPath $thresholdPidFile) {
    $thresholdOldPid = [int](Get-Content -LiteralPath $thresholdPidFile -Raw)
    $thresholdExisting = Get-CimInstance Win32_Process -Filter "ProcessId = $thresholdOldPid" -ErrorAction SilentlyContinue
    if ($thresholdExisting -and $thresholdExisting.CommandLine -like '*watch_validation.py*') {
        Write-Output "Validation watcher already running: PID $thresholdOldPid"
        exit 0
    }
}
$thresholdStopFile = Join-Path $thresholdDirectory 'threshold_watch.stop'
if (Test-Path -LiteralPath $thresholdStopFile) { Remove-Item -LiteralPath $thresholdStopFile }
$thresholdPython = (Get-Command python -ErrorAction Stop).Source
$thresholdWatchScript = Join-Path $thresholdDirectory 'watch_validation.py'
$thresholdProcess = Start-Process -FilePath $thresholdPython -ArgumentList @('-u', $thresholdWatchScript) -WorkingDirectory $thresholdDirectory -WindowStyle Hidden -RedirectStandardOutput (Join-Path $thresholdDirectory 'threshold_watch.log') -RedirectStandardError (Join-Path $thresholdDirectory 'threshold_watch.stderr.log') -PassThru
Set-Content -LiteralPath $thresholdPidFile -Value $thresholdProcess.Id -Encoding ascii
Write-Output "Validation watcher started hidden: PID $($thresholdProcess.Id); checks local artifacts every 60 seconds."
