Enable-PSRemoting -Verbose
Invoke-WebRequest -UseBasicParsing -Uri "${PINGBACK_URL}" -Verbose
