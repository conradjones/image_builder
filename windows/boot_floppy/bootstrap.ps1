Enable-PSRemoting -force
$Args = @('set', 'winrm/config/service/auth', '@{Basic="true";}')
Start-Process -FilePath "c:\windows\system32\winrm.cmd" -ArgumentList $Args
$Args = @('set', 'winrm/config/service', '@{AllowUnenrypted="true";}')
Start-Process -FilePath "c:\windows\system32\winrm.cmd" -ArgumentList $Args
Invoke-WebRequest -UseBasicParsing -Uri "${PINGBACK_URL}"
