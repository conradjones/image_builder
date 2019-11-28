$Folder = "C:\.winstall"
if (!(Test-Path -Path $Folder)) {
    New-Item -Path $Folder -ItemType Directory | Out-Null
}
