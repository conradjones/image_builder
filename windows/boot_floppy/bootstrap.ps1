$LocalIP = netsh interface ip show  addresses "Ethernet0" | Select-String "IP Address"
$LocalIP = [regex]::Match($LocalIP, 'IP Address:.*\b([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})').Groups[1].Value
Invoke-WebRequest -UseBasicParsing -Uri "${PINGBACK_URL}/pingback/$LocalIP" -Verbose
