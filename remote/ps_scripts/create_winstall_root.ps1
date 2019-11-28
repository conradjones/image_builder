$Folder = "C:\.winstall"
if (!(Test-Path -Path $Folder)) {
    New-Item -Path $Folder -ItemType Directory | Out-Null
}
$Folder = "C:\.winstall\transfer"
if (!(Test-Path -Path $Folder)) {
    New-Item -Path $Folder -ItemType Directory | Out-Null
}
$Folder = "C:\.winstall\packages"
if (!(Test-Path -Path $Folder)) {
    New-Item -Path $Folder -ItemType Directory | Out-Null
}
