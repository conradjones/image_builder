$LocalIP = ipconfig | Select-String "IPv4 Address"
$LocalIP = [regex]::Match($LocalIP, '([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})').Groups[1].Value
Invoke-WebRequest -UseBasicParsing -Uri "${PINGBACK_URL}/pingback/$LocalIP" -Verbose
