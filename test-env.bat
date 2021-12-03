for /f "delims=" %%i in ('docker-compose --version') do set output=%%i
echo %output%|find "v2" >nul
if errorlevel 1 (docker-compose up) else (docker-compose --env-file .empty.env up)