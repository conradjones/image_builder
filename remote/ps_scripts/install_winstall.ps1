# TODO pass install location as param
$Url = "https://github.com/conradjones/winstall/archive/master.zip"
$InstallPath = "C:\.winstall"

$FileName = $Url  | Split-Path -Leaf
$Output = Join-Path -Path $InstallPath -ChildPath $FileName

$WebClient = New-Object System.Net.WebClient
"Downloading:$Url" | Out-Host
$WebClient.DownloadFile($Url, $Output)

Expand-Archive -LiteralPath $Output -DestinationPath $InstallPath