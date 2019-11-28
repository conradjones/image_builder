mkdir c:\ImageBuild

call c:\windows\system32\winrm.cmd set winrm/config/service/auth @{Basic="true"} >> c:\ImageBuild\imagebuild.log 2>&1
call c:\windows\system32\winrm.cmd set winrm/config/service @{AllowUnenrypted="true"} >> c:\ImageBuild\imagebuild.log 2>&1

powershell.exe -executionpolicy bypass -file "a:\bootstrap.ps1" > c:\ImageBuild\imagebuild.log 2>>&1